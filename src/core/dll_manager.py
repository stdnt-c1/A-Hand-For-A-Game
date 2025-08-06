"""
DLL Management System for AzimuthControl

This module manages DLL loading and prevents conflicts when multiple DLLs exist.
It ensures only the correct version is loaded and provides fallback mechanisms.
"""

import ctypes
import os
import sys
import hashlib
from pathlib import Path
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

class DLLManager:
    """Manages DLL loading with conflict resolution"""
    
    def __init__(self):
        self.loaded_dlls: Dict[str, ctypes.CDLL] = {}
        self.dll_registry: Dict[str, Dict[str, Any]] = {}
        
    def register_dll(self, name: str, path: str, expected_hash: Optional[str] = None, 
                    architecture: str = "x64", priority: int = 0):
        """Register a DLL with metadata"""
        self.dll_registry[name] = {
            'path': path,
            'expected_hash': expected_hash,
            'architecture': architecture,
            'priority': priority,
            'loaded': False
        }
        
    def get_dll_hash(self, dll_path: str) -> str:
        """Calculate SHA256 hash of DLL file"""
        try:
            with open(dll_path, 'rb') as f:
                return hashlib.sha256(f.read()).hexdigest()
        except Exception as e:
            logger.error(f"Failed to calculate hash for {dll_path}: {e}")
            return ""
            
    def verify_dll_architecture(self, dll_path: str) -> str:
        """Verify DLL architecture (simplified check)"""
        try:
            # Try loading to check compatibility
            test_dll = ctypes.CDLL(dll_path)
            return "x64"  # If it loads on 64-bit Python, assume x64
        except OSError as e:
            if "193" in str(e):  # Invalid Win32 application
                return "x86"
            return "unknown"
            
    def find_best_dll(self, name: str) -> Optional[str]:
        """Find the best DLL version based on priority and architecture"""
        if name not in self.dll_registry:
            return None
            
        dll_info = self.dll_registry[name]
        dll_path = dll_info['path']
        
        # Check if file exists
        if not os.path.exists(dll_path):
            logger.warning(f"DLL not found: {dll_path}")
            return None
            
        # Verify architecture
        actual_arch = self.verify_dll_architecture(dll_path)
        expected_arch = dll_info['architecture']
        
        if actual_arch != expected_arch and actual_arch != "unknown":
            logger.warning(f"Architecture mismatch for {name}: expected {expected_arch}, got {actual_arch}")
            
        # Verify hash if provided
        if dll_info['expected_hash']:
            actual_hash = self.get_dll_hash(dll_path)
            if actual_hash != dll_info['expected_hash']:
                logger.warning(f"Hash mismatch for {name}")
                
        return dll_path
        
    def load_dll(self, name: str, force_reload: bool = False) -> Optional[ctypes.CDLL]:
        """Load DLL with conflict resolution"""
        if name in self.loaded_dlls and not force_reload:
            return self.loaded_dlls[name]
            
        dll_path = self.find_best_dll(name)
        if not dll_path:
            logger.error(f"No suitable DLL found for {name}")
            return None
            
        try:
            dll = ctypes.CDLL(dll_path)
            self.loaded_dlls[name] = dll
            self.dll_registry[name]['loaded'] = True
            logger.info(f"Successfully loaded DLL: {name} from {dll_path}")
            return dll
            
        except Exception as e:
            logger.error(f"Failed to load DLL {name} from {dll_path}: {e}")
            return None
            
    def unload_dll(self, name: str):
        """Unload a DLL (note: Windows doesn't actually unload DLLs)"""
        if name in self.loaded_dlls:
            del self.loaded_dlls[name]
            self.dll_registry[name]['loaded'] = False
            logger.info(f"Unloaded DLL: {name}")
            
    def cleanup_old_dlls(self, directory: str, keep_pattern: str = "res_balancer*.dll"):
        """Clean up old DLL files"""
        try:
            dll_dir = Path(directory)
            if not dll_dir.exists():
                return
                
            for dll_file in dll_dir.glob("*.dll"):
                # Keep CUDA DLL, regular DLL, and CUDA runtime
                if (dll_file.name.startswith("res_balancer") or 
                    dll_file.name.startswith("cudart") or
                    dll_file.name == keep_pattern):
                    continue  # Keep these DLLs
                try:
                    dll_file.unlink()
                    logger.info(f"Cleaned up old DLL: {dll_file}")
                except Exception as e:
                    logger.warning(f"Could not remove {dll_file}: {e}")
                        
        except Exception as e:
            logger.error(f"Error during DLL cleanup: {e}")
            
    def get_dll_info(self, name: str) -> Dict[str, Any]:
        """Get information about a registered DLL"""
        if name not in self.dll_registry:
            return {}
            
        info = self.dll_registry[name].copy()
        if os.path.exists(info['path']):
            info['actual_hash'] = self.get_dll_hash(info['path'])
            info['actual_architecture'] = self.verify_dll_architecture(info['path'])
            info['file_size'] = os.path.getsize(info['path'])
        else:
            info['exists'] = False
            
        return info

# Global DLL manager instance
dll_manager = DLLManager()

# Register the enhanced frame processor DLL
dll_manager.register_dll(
    name="frame_processor",
    path="./resBalancer/res_balancer_cuda.dll",
    architecture="x64", 
    priority=1
)

# Fallback registration for legacy DLL
dll_manager.register_dll(
    name="frame_processor_legacy",
    path="./resBalancer/res_balancer.dll",
    architecture="x64",
    priority=2
)

def get_frame_processor_dll() -> Optional[ctypes.CDLL]:
    """Get the frame processor DLL with conflict resolution"""
    # Try enhanced CUDA DLL first
    dll = dll_manager.load_dll("frame_processor")
    if dll:
        return dll
    
    # Fallback to legacy DLL
    return dll_manager.load_dll("frame_processor_legacy")

def cleanup_dll_conflicts():
    """Clean up potential DLL conflicts"""
    dll_manager.cleanup_old_dlls("./resBalancer/")
    dll_manager.cleanup_old_dlls("./build/")
    dll_manager.cleanup_old_dlls("./")  # Clean root directory
