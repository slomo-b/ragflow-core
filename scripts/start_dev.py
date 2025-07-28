import subprocess
import sys
import os
import time
import json
from pathlib import Path
import shutil
import logging
from datetime import datetime

# Configure logging with UTF-8 encoding
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class RagFlowDevEnvironment:
    def __init__(self):
        self.project_root = Path.cwd()
        self.compose_file = self.project_root / "docker" / "docker-compose.dev.yml"
        self.backup_dir = self.project_root / ".ragflow_backups"
        
        # Extended timeout for slow builds
        self.build_timeout = 300  # 5 minutes instead of 60 seconds
        self.start_timeout = 180  # 3 minutes for startup
        
    def run_command(self, cmd, timeout=None, cwd=None, capture_output=True):
        """Run command with proper encoding handling for Windows"""
        try:
            # Use UTF-8 encoding and handle Windows cmd issues
            process = subprocess.run(
                cmd,
                cwd=cwd or self.project_root,
                capture_output=capture_output,
                text=True,
                timeout=timeout,
                encoding='utf-8',
                errors='replace',  # Replace problematic characters instead of failing
                shell=True if sys.platform == "win32" else False
            )
            return process
        except subprocess.TimeoutExpired:
            logger.error(f"❌ Command timed out after {timeout}s: {' '.join(cmd)}")
            raise
        except UnicodeDecodeError as e:
            logger.error(f"❌ Unicode decode error: {e}")
            raise
        except Exception as e:
            logger.error(f"❌ Unexpected error: {e}")
            raise

    def check_system_requirements(self):
        """Check system requirements"""
        logger.info("🔍 Checking system requirements...")
        requirements_met = True
        
        # Check Docker
        try:
            result = self.run_command(["docker", "--version"], timeout=10)
            if result.returncode == 0:
                logger.info(f"✅ Docker: {result.stdout.strip()}")
            else:
                logger.error("❌ Docker not found or not running")
                requirements_met = False
        except Exception:
            logger.error("❌ Docker not found or not running")
            requirements_met = False
            
        # Check Docker Compose
        try:
            result = self.run_command(["docker", "compose", "version"], timeout=10)
            if result.returncode == 0:
                logger.info(f"✅ Docker Compose: {result.stdout.strip()}")
            else:
                logger.error("❌ Docker Compose not found")
                requirements_met = False
        except Exception:
            logger.error("❌ Docker Compose not found")
            requirements_met = False
            
        # Check available disk space
        try:
            if sys.platform == "win32":
                import shutil
                free_space = shutil.disk_usage('.').free / (1024**3)  # GB
            else:
                statvfs = os.statvfs('.')
                free_space = statvfs.f_frsize * statvfs.f_bavail / (1024**3)  # GB
                
            if free_space < 10:
                logger.warning(f"⚠️  Disk Space: {free_space:.1f}GB free (10GB+ recommended)")
                requirements_met = False
            else:
                logger.info(f"✅ Disk Space: {free_space:.1f}GB free")
        except Exception:
            logger.warning("⚠️  Could not check disk space")
            
        # Check CPU cores
        try:
            import multiprocessing
            cpu_count = multiprocessing.cpu_count()
            if cpu_count >= 2:
                logger.info(f"✅ CPU: {cpu_count} cores")
            else:
                logger.warning(f"⚠️  CPU: {cpu_count} core (2+ recommended)")
                requirements_met = False
        except Exception:
            logger.warning("⚠️  Could not check CPU count")
            
        # Check platform
        import platform
        logger.info(f"✅ Platform: {platform.system()} {platform.release()}")
        
        # Check Python version
        python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
        logger.info(f"✅ Python: {python_version}")
        
        if not requirements_met:
            logger.warning("⚠️ Some system requirements are not met.")
            logger.warning("The environment may not work optimally.")
            
        return requirements_met

    def create_backup(self):
        """Create backup of critical files"""
        logger.info("💾 Creating backup of critical files...")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = self.backup_dir / f"backup_{timestamp}"
        backup_path.mkdir(parents=True, exist_ok=True)
        
        critical_files = [
            "docker/docker-compose.dev.yml",
            "backend/requirements.txt",
            "backend/app/main.py",
            "frontend/package.json"
        ]
        
        for file_path in critical_files:
            src = self.project_root / file_path
            if src.exists():
                dst = backup_path / file_path
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, dst)
                logger.info(f"Backed up: {file_path}")
        
        logger.info(f"✅ Backup created: {backup_path}")
        return backup_path

    def check_compose_file(self):
        """Check if compose file exists"""
        if not self.compose_file.exists():
            logger.error(f"❌ Docker compose file not found: {self.compose_file}")
            return False
        
        logger.info(f"✅ Using Docker Compose file: {self.compose_file}")
        return True

    def build_services_with_retry(self, service=None, max_retries=2):
        """Build services with retry logic and extended timeout"""
        for attempt in range(max_retries + 1):
            try:
                if service:
                    logger.info(f"🔨 Building {service} (attempt {attempt + 1}/{max_retries + 1})...")
                    cmd = ["docker", "compose", "-f", str(self.compose_file), "build", "--no-cache", service]
                else:
                    logger.info(f"🔨 Building all services (attempt {attempt + 1}/{max_retries + 1})...")
                    cmd = ["docker", "compose", "-f", str(self.compose_file), "build", "--no-cache"]
                
                result = self.run_command(cmd, timeout=self.build_timeout, capture_output=False)
                
                if result.returncode == 0:
                    logger.info(f"✅ Build successful!")
                    return True
                else:
                    logger.error(f"❌ Build failed with return code {result.returncode}")
                    if attempt < max_retries:
                        logger.info("🔄 Retrying build...")
                        time.sleep(5)
                    
            except subprocess.TimeoutExpired:
                logger.error(f"❌ Build timed out after {self.build_timeout}s")
                if attempt < max_retries:
                    logger.info("🔄 Retrying with longer timeout...")
                    self.build_timeout += 120  # Add 2 more minutes each retry
                    time.sleep(10)
                else:
                    logger.error("❌ Build failed after all retries")
                    return False
            except Exception as e:
                logger.error(f"❌ Build error: {e}")
                if attempt < max_retries:
                    logger.info("🔄 Retrying build...")
                    time.sleep(5)
                else:
                    return False
        
        return False

    def start_infrastructure_services(self):
        """Start infrastructure services first"""
        logger.info("⏳ Starting infrastructure services...")
        
        infrastructure = ["postgres", "qdrant", "redis"]
        cmd = ["docker", "compose", "-f", str(self.compose_file), "up", "-d"] + infrastructure
        
        try:
            result = self.run_command(cmd, timeout=60, capture_output=False)
            if result.returncode != 0:
                logger.error("❌ Failed to start infrastructure services")
                return False
                
            # Wait for services to be healthy
            logger.info("⏳ Waiting for infrastructure services to be healthy...")
            time.sleep(30)  # Give services time to start
            
            # Check if services are running
            for service in infrastructure:
                check_cmd = ["docker", "compose", "-f", str(self.compose_file), "ps", service]
                result = self.run_command(check_cmd, timeout=10)
                if "Up" not in result.stdout:
                    logger.warning(f"⚠️  {service} may not be fully ready")
            
            logger.info("✅ Infrastructure services started")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error starting infrastructure: {e}")
            return False

    def smart_service_startup(self):
        """Smart startup with dependency management"""
        logger.info("🚀 Smart service startup with dependency management...")
        
        # Start infrastructure first
        if not self.start_infrastructure_services():
            return False
        
        # Check if backend needs rebuild
        logger.info("🔄 Checking if backend needs rebuild...")
        
        # For now, always rebuild to ensure latest changes
        logger.info("🔄 Backend: requirements may have changed, rebuild recommended")
        
        # Build backend with retry
        if not self.build_services_with_retry("backend"):
            logger.error("❌ Failed to build backend after retries")
            return False
        
        # Start backend
        logger.info("🚀 Starting backend...")
        cmd = ["docker", "compose", "-f", str(self.compose_file), "up", "-d", "backend"]
        try:
            result = self.run_command(cmd, timeout=self.start_timeout, capture_output=False)
            if result.returncode != 0:
                logger.error("❌ Failed to start backend")
                return False
        except Exception as e:
            logger.error(f"❌ Error starting backend: {e}")
            return False
        
        # Check if frontend exists and start it
        if (self.project_root / "frontend").exists():
            logger.info("🚀 Starting frontend...")
            cmd = ["docker", "compose", "-f", str(self.compose_file), "up", "-d", "frontend"]
            try:
                result = self.run_command(cmd, timeout=self.start_timeout, capture_output=False)
                if result.returncode != 0:
                    logger.warning("⚠️  Frontend failed to start (this is okay if not implemented yet)")
            except Exception as e:
                logger.warning(f"⚠️  Frontend startup error: {e}")
        
        return True

    def show_service_status(self):
        """Show status of all services"""
        logger.info("📊 Service Status:")
        
        try:
            cmd = ["docker", "compose", "-f", str(self.compose_file), "ps"]
            result = self.run_command(cmd, timeout=30)
            if result.returncode == 0:
                print(result.stdout)
            else:
                logger.error("❌ Could not get service status")
        except Exception as e:
            logger.error(f"❌ Error getting service status: {e}")

    def show_access_info(self):
        """Show access information"""
        logger.info("🌐 Access Information:")
        print("=" * 60)
        print("🔗 Backend API: http://localhost:8000")
        print("📚 API Docs: http://localhost:8000/docs")
        print("🔍 Qdrant Dashboard: http://localhost:6333/dashboard")
        if (self.project_root / "frontend").exists():
            print("🎨 Frontend: http://localhost:3000")
        print("=" * 60)
        print()
        print("🔧 Useful Commands:")
        print("  View logs: docker compose -f docker/docker-compose.dev.yml logs -f")
        print("  Stop all: docker compose -f docker/docker-compose.dev.yml down")
        print("  Restart: docker compose -f docker/docker-compose.dev.yml restart")

    def run(self):
        """Main execution method"""
        print("🚀 RagFlow Enhanced Development Environment v2.1")
        print("=" * 60)
        
        # Check system requirements
        self.check_system_requirements()
        
        # Create backup
        self.create_backup()
        
        # Check compose file
        if not self.check_compose_file():
            return False
        
        # Smart startup
        if not self.smart_service_startup():
            logger.error("❌ Failed to start services")
            return False
        
        # Wait a bit for services to settle
        logger.info("⏳ Waiting for services to settle...")
        time.sleep(15)
        
        # Show status
        self.show_service_status()
        
        # Show access info
        self.show_access_info()
        
        logger.info("✅ RagFlow development environment is ready!")
        return True

def main():
    """Main entry point"""
    try:
        env = RagFlowDevEnvironment()
        success = env.run()
        
        if not success:
            logger.error("❌ Failed to start development environment")
            sys.exit(1)
            
    except KeyboardInterrupt:
        logger.info("👋 Interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()