#!/usr/bin/python3
"""
Simple camera test to isolate the Remote I/O error
"""
import time
import sys

def test_libcamera_first():
    """Test with libcamera-hello first"""
    print("=== Testing with libcamera-hello ===")
    import subprocess
    
    try:
        # Test camera detection
        result = subprocess.run(['libcamera-hello', '--list-cameras'], 
                              capture_output=True, text=True, timeout=10)
        print("Camera detection output:")
        print(result.stdout)
        if result.stderr:
            print("Errors:")
            print(result.stderr)
        
        # Try a quick capture test
        print("\nTrying quick capture test...")
        result = subprocess.run(['libcamera-hello', '--timeout', '2000'], 
                              capture_output=True, text=True, timeout=15)
        
        if result.returncode == 0:
            print("✅ libcamera-hello test PASSED")
            return True
        else:
            print("❌ libcamera-hello test FAILED")
            print("STDOUT:", result.stdout)
            print("STDERR:", result.stderr)
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ libcamera-hello timed out")
        return False
    except Exception as e:
        print(f"❌ Error running libcamera-hello: {e}")
        return False

def test_picamera2_step_by_step():
    """Test Picamera2 initialization step by step"""
    print("\n=== Testing Picamera2 Step by Step ===")
    
    try:
        print("1. Importing Picamera2...")
        from picamera2 import Picamera2
        print("✅ Import successful")
        
        print("2. Getting camera info...")
        camera_info = Picamera2.global_camera_info()
        print(f"✅ Found {len(camera_info)} cameras")
        for i, info in enumerate(camera_info):
            print(f"   Camera {i}: {info}")
        
        print("3. Creating Picamera2 instance...")
        picam2 = Picamera2()
        print("✅ Instance created")
        
        print("4. Getting camera properties...")
        props = picam2.camera_properties
        print(f"✅ Camera properties: {props}")
        
        print("5. Creating simple still configuration...")
        config = picam2.create_still_configuration(main={"size": (640, 480)})
        print(f"✅ Configuration created: {config}")
        
        print("6. Applying configuration...")
        picam2.configure(config)
        print("✅ Configuration applied")
        
        print("7. Starting camera...")
        picam2.start()
        print("✅ Camera started successfully!")
        
        print("8. Sleeping for 2 seconds...")
        time.sleep(2)
        
        print("9. Stopping camera...")
        picam2.stop()
        print("✅ Camera stopped")
        
        print("10. Closing camera...")
        picam2.close()
        print("✅ Camera closed")
        
        print("\n🎉 SUCCESS: All tests passed!")
        return True
        
    except Exception as e:
        print(f"\n❌ FAILED at step: {e}")
        print(f"Error type: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        return False

def test_different_configurations():
    """Test with different camera configurations"""
    print("\n=== Testing Different Configurations ===")
    
    try:
        from picamera2 import Picamera2
        
        configurations = [
            {"name": "Minimal 320x240", "size": (320, 240)},
            {"name": "Small 640x480", "size": (640, 480)},
            {"name": "Your target 236x236", "size": (236, 236)},
        ]
        
        for config_info in configurations:
            print(f"\nTesting {config_info['name']}...")
            
            try:
                picam2 = Picamera2()
                config = picam2.create_still_configuration(
                    main={"size": config_info['size']}
                )
                picam2.configure(config)
                picam2.start()
                time.sleep(1)
                picam2.stop()
                picam2.close()
                print(f"✅ {config_info['name']} - SUCCESS")
                
            except Exception as e:
                print(f"❌ {config_info['name']} - FAILED: {e}")
                try:
                    picam2.close()
                except:
                    pass
                    
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")

def main():
    print("SIMPLE CAMERA DIAGNOSTIC TEST")
    print("=" * 50)
    
    # Test 1: libcamera-hello
    libcamera_ok = test_libcamera_first()
    
    if not libcamera_ok:
        print("\n❌ libcamera-hello failed - this indicates a hardware problem")
        print("Please check:")
        print("1. Camera cable connection")
        print("2. Power supply (use official Pi power adapter)")
        print("3. Boot configuration (/boot/config.txt)")
        print("4. Try: sudo modprobe bcm2835_v4l2")
        return
    
    # Test 2: Picamera2 step by step
    picamera2_ok = test_picamera2_step_by_step()
    
    if picamera2_ok:
        # Test 3: Different configurations
        test_different_configurations()
        
        print("\n" + "=" * 50)
        print("🎉 ALL TESTS PASSED!")
        print("Your camera hardware is working.")
        print("The issue might be specific to your streaming configuration.")
        print("Try the updated MJPEG script with error handling.")
        
    else:
        print("\n" + "=" * 50)
        print("❌ PICAMERA2 TESTS FAILED")
        print("Even though libcamera-hello works, Picamera2 is failing.")
        print("This could be due to:")
        print("1. Python environment issues")
        print("2. Picamera2 version compatibility")
        print("3. System configuration")
        print("\nTry:")
        print("pip install --upgrade picamera2")
        print("sudo apt update && sudo apt upgrade")

if __name__ == "__main__":
    main()
