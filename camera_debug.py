#!/usr/bin/python3
"""
Advanced camera hardware debugging for Remote I/O errors
"""
import os
import sys
import subprocess
import time

def run_command(cmd, description=""):
    """Run a command and return its output"""
    print(f"\n{'='*50}")
    if description:
        print(f"Running: {description}")
    print(f"Command: {cmd}")
    print("-" * 30)
    
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
        if result.stdout:
            print("STDOUT:")
            print(result.stdout)
        if result.stderr:
            print("STDERR:")
            print(result.stderr)
        print(f"Return code: {result.returncode}")
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        print("Command timed out!")
        return False, "", "Timeout"
    except Exception as e:
        print(f"Error running command: {e}")
        return False, "", str(e)

def check_camera_hardware():
    """Check camera hardware detection"""
    print("CAMERA HARDWARE DIAGNOSTICS")
    print("=" * 60)
    
    # Check if camera is detected by the system
    run_command("lsusb", "USB devices")
    run_command("dmesg | grep -i camera", "Camera-related kernel messages")
    run_command("dmesg | grep -i ov5647", "OV5647 sensor messages")
    run_command("dmesg | grep -i csi", "CSI interface messages")
    
    # Check video devices
    run_command("ls -la /dev/video*", "Video devices")
    run_command("v4l2-ctl --list-devices", "V4L2 devices")
    
    # Check libcamera detection
    run_command("libcamera-hello --list-cameras", "libcamera camera detection")
    
    # Check for I2C issues
    run_command("i2cdetect -y 1", "I2C bus scan")
    
    # Check GPU memory
    run_command("vcgencmd get_mem gpu", "GPU memory allocation")
    
    # Check camera-specific boot messages
    run_command("dmesg | grep -i 'remote i/o'", "Remote I/O error messages")
    run_command("dmesg | grep -i 'unicam'", "Unicam driver messages")
    run_command("dmesg | grep -i 'v4l2'", "V4L2 messages")

def check_power_and_connections():
    """Check power supply and connections"""
    print("\n" + "=" * 60)
    print("POWER AND CONNECTION DIAGNOSTICS")
    print("=" * 60)
    
    # Check power supply
    run_command("vcgencmd get_throttled", "Power/thermal throttling status")
    run_command("vcgencmd measure_volts", "Voltage measurements")
    run_command("vcgencmd measure_temp", "Temperature")
    
    # Check for under-voltage warnings
    run_command("dmesg | grep -i 'under-voltage'", "Under-voltage warnings")
    run_command("dmesg | grep -i 'voltage'", "All voltage-related messages")

def test_camera_initialization():
    """Test camera with different approaches"""
    print("\n" + "=" * 60)
    print("CAMERA INITIALIZATION TESTS")
    print("=" * 60)
    
    # Test with libcamera-hello
    print("\nTesting with libcamera-hello (5 second test)...")
    success, stdout, stderr = run_command("timeout 5 libcamera-hello --verbose", "libcamera-hello test")
    
    if not success:
        print("libcamera-hello failed - this confirms hardware issue")
    
    # Test with different camera modes
    print("\nTesting camera with minimal settings...")
    test_script = """
import sys
try:
    from picamera2 import Picamera2
    import time
    
    print("Creating Picamera2 instance...")
    picam2 = Picamera2()
    
    print("Available cameras:")
    for i, info in enumerate(Picamera2.global_camera_info()):
        print(f"Camera {i}: {info}")
    
    print("Getting camera properties...")
    props = picam2.camera_properties
    print(f"Camera properties: {props}")
    
    print("Creating minimal configuration...")
    config = picam2.create_still_configuration(main={"size": (640, 480)})
    print(f"Configuration: {config}")
    
    print("Configuring camera...")
    picam2.configure(config)
    
    print("Starting camera...")
    picam2.start()
    
    print("Camera started successfully!")
    time.sleep(2)
    
    print("Stopping camera...")
    picam2.stop()
    picam2.close()
    
    print("SUCCESS: Camera test completed without errors")
    
except Exception as e:
    print(f"ERROR: {e}")
    print(f"Error type: {type(e).__name__}")
    import traceback
    traceback.print_exc()
"""
    
    # Write test script to temp file
    with open('/tmp/camera_test.py', 'w') as f:
        f.write(test_script)
    
    run_command("python3 /tmp/camera_test.py", "Minimal camera test")
    
    # Clean up
    try:
        os.remove('/tmp/camera_test.py')
    except:
        pass

def check_system_resources():
    """Check system resources that might affect camera"""
    print("\n" + "=" * 60)
    print("SYSTEM RESOURCES")
    print("=" * 60)
    
    run_command("free -h", "Memory usage")
    run_command("df -h", "Disk usage")
    run_command("lsmod | grep -i camera", "Camera-related kernel modules")
    run_command("lsmod | grep -i v4l2", "V4L2 modules")
    run_command("lsmod | grep -i bcm2835", "BCM2835 modules")

def suggest_fixes():
    """Suggest potential fixes based on common issues"""
    print("\n" + "=" * 60)
    print("SUGGESTED FIXES FOR 'Remote I/O Error'")
    print("=" * 60)
    
    fixes = [
        "1. POWER SUPPLY ISSUES:",
        "   - Use official Pi power supply (5V 3A for Pi 4/5)",
        "   - Check for under-voltage warnings in dmesg",
        "   - Try a different power cable",
        "",
        "2. CAMERA CABLE CONNECTION:",
        "   - Power off Pi completely",
        "   - Disconnect and reconnect camera cable",
        "   - Ensure cable is fully inserted and locked",
        "   - Try a different camera cable if available",
        "   - Check cable orientation (blue side toward USB ports on Pi)",
        "",
        "3. BOOT CONFIG ISSUES:",
        "   - Add/modify in /boot/firmware/config.txt or /boot/config.txt:",
        "     camera_auto_detect=1",
        "     gpu_mem=128",
        "     gpu_mem_256=128",
        "     gpu_mem_512=128",
        "     gpu_mem_1024=128",
        "",
        "4. DRIVER/MODULE ISSUES:",
        "   - sudo modprobe -r bcm2835_v4l2",
        "   - sudo modprobe bcm2835_v4l2",
        "   - sudo systemctl restart systemd-modules-load",
        "",
        "5. CAMERA MODULE ISSUES:",
        "   - Try a different camera module if available",
        "   - Some cheap camera modules are faulty",
        "",
        "6. INTERFERENCE:",
        "   - Remove any other USB devices",
        "   - Try without other HATs or add-ons",
        "",
        "7. REBOOT AND RETRY:",
        "   - sudo reboot",
        "   - Wait 30 seconds before testing",
        "",
        "8. DOWNGRADE LIBCAMERA (if recently updated):",
        "   - sudo apt update && sudo apt install --reinstall libcamera*",
    ]
    
    for fix in fixes:
        print(fix)

def main():
    print("RASPBERRY PI CAMERA 'Remote I/O Error' DIAGNOSTICS")
    print("=" * 70)
    print("This script will help diagnose hardware-related camera issues")
    print("=" * 70)
    
    check_camera_hardware()
    check_power_and_connections()
    check_system_resources()
    test_camera_initialization()
    suggest_fixes()
    
    print("\n" + "=" * 70)
    print("DIAGNOSIS COMPLETE")
    print("=" * 70)
    print("Review the output above and try the suggested fixes.")
    print("The most common causes are:")
    print("1. Inadequate power supply")
    print("2. Loose camera cable connection")
    print("3. Faulty camera module")
    print("4. Insufficient GPU memory allocation")

if __name__ == "__main__":
    main()
