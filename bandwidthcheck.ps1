# Define the threshold for network speed (in Mbps)
$threshold = 1000

# Log file path
$logFilePath = "C:\Users\manoj.kalluru\OneDrive - Qentelli\Desktop\network_log.txt"

# Function to log messages with timestamp
function Log-Message {
    param (
        [string]$message
    )
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    Add-Content -Path $logFilePath -Value "$timestamp - $message"
}

# Function to check network speed
function Check-NetworkSpeed {
    $netAdapter = Get-NetAdapter | Where-Object {$_.Status -eq "Up"}
    if ($netAdapter) {
        # Extract and convert the speed from the LinkSpeed property
        $linkSpeed = [double]($netAdapter.LinkSpeed -replace ' Mbps', '')

        if ($linkSpeed -lt $threshold) {
            $message = "Internet connectivity is poor. Please switch to a better network."
            Log-Message $message
            # Use the Windows Forms message box instead of WPF
            Add-Type -AssemblyName PresentationFramework
            [System.Windows.MessageBox]::Show($message, "Network Alert", 'OK', 'Warning')
        }
    } else {
        Log-Message "No active network adapter found."
    }
}

# Function to handle network change events
function NetworkChange-Event {
    $message = "NETWORK CHANGE DETECTED"
    Log-Message $message
    Add-Type -AssemblyName PresentationFramework
    [System.Windows.MessageBox]::Show($message, "Network Alert", 'OK', 'Warning')
    Check-NetworkSpeed
}

# Register the network change event
Register-ObjectEvent -InputObject ([System.Net.NetworkInformation.NetworkChange]) `
    -EventName "NetworkAddressChanged" `
    -Action { NetworkChange-Event }

# Continuous monitoring loop
while ($true) {
    Check-NetworkSpeed
    Start-Sleep -Seconds 30  # Adjust the interval as needed
}
