import pytest
from emotiv_lsl.service.linux_adapter import LinuxServiceAdapter

def test_generate_service_unit_content_defaults():
    """Test _generate_service_unit_content with default keyword arguments."""
    adapter = LinuxServiceAdapter("test-service", "Test Service", "A test service description")
    content = adapter._generate_service_unit_content("/usr/bin/python3", "testuser", "testgroup")

    assert "Description=A test service description" in content
    assert "User=testuser" in content
    assert "Group=testgroup" in content
    assert "WorkingDirectory=/opt/emotiv-lsl" in content
    assert "ExecStart=/usr/bin/python3 -m emotiv_lsl.service" in content
    assert "Restart=always" in content
    assert "RestartSec=10" in content
    # Ensure no Environment= lines are present if none are provided
    assert "Environment=" not in content

def test_generate_service_unit_content_custom_params():
    """Test _generate_service_unit_content with custom working directory and restart settings."""
    adapter = LinuxServiceAdapter("test-service", "Test Service", "A test service description")
    content = adapter._generate_service_unit_content(
        "/usr/bin/python3", "testuser", "testgroup",
        working_directory="/home/user/app",
        restart_policy="on-failure",
        restart_delay="5"
    )

    assert "WorkingDirectory=/home/user/app" in content
    assert "Restart=on-failure" in content
    assert "RestartSec=5" in content

def test_generate_service_unit_content_environment():
    """Test _generate_service_unit_content with environment variables."""
    adapter = LinuxServiceAdapter("test-service", "Test Service", "A test service description")
    content = adapter._generate_service_unit_content(
        "/usr/bin/python3", "testuser", "testgroup",
        environment={"KEY1": "VAL1", "KEY2": "VAL2"}
    )

    assert "Environment=KEY1=VAL1" in content
    assert "Environment=KEY2=VAL2" in content
    # Check if they are on separate lines
    assert "Environment=KEY1=VAL1\nEnvironment=KEY2=VAL2" in content
