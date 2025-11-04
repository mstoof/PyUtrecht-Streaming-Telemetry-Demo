"""
PyUtrecht Presentation: Streaming Telemetry Demo
Complete demo with gNMI and gRPC using Arista cEOS in Containerlab
Compatible with PyGNMI 0.8.15
By: Maurice Stoof
Date: Nov 2025
"""

from pygnmi.client import gNMIclient
import json
import time
from datetime import datetime
from collections import defaultdict


class Colors:
    """ANSI color codes for terminal output"""
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'


class TelemetryDemo:
    """Streaming telemetry demonstration"""
    
    def __init__(self, host='172.20.20.11', port=6030):
        self.host = host
        self.port = port
        self.client = None
        self.stats = defaultdict(lambda: {'rx_bytes': 0, 'tx_bytes': 0, 'updates': 0})
        
    def print_header(self, text):
        """Print colored header"""
        print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*70}{Colors.END}")
        print(f"{Colors.BOLD}{Colors.CYAN}{text.center(70)}{Colors.END}")
        print(f"{Colors.BOLD}{Colors.CYAN}{'='*70}{Colors.END}\n")
    
    def print_step(self, step, text):
        """Print step information"""
        print(f"{Colors.BOLD}{Colors.GREEN}[Step {step}]{Colors.END} {text}")
    
    def connect(self):
        """Establish connection to Arista switch"""
        self.print_step(1, f"Connecting to Arista cEOS at {self.host}:{self.port}...")
        
        try:
            self.client = gNMIclient(
                target=(self.host, self.port),
                username='admin',
                password='admin',
                insecure=True
            )
            # Force connection
            self.client.connect()
            print(f"{Colors.GREEN}✓ Connected successfully!{Colors.END}\n")
            return True
        except Exception as e:
            print(f"{Colors.RED}✗ Connection failed: {e}{Colors.END}")
            return False
    
    def demo_capabilities(self):
        """Demo 1: Show device capabilities"""
        self.print_header("DEMO 1: Device Capabilities (gNMI)")
        
        self.print_step(2, "Requesting device capabilities...")
        
        try:
            capabilities = self.client.capabilities()
            
            print(f"\n{Colors.YELLOW}Device Information:{Colors.END}")
            # Handle different response formats for supported encodings
            encodings = capabilities.get('supported_encodings', [])
            if encodings:
                encoding_names = [str(e) for e in encodings]

            models = capabilities.get('supported_models', [])
            if models:
                print(f"\n{Colors.YELLOW}Supported YANG Models:{Colors.END}")
                for model in models[:5]:  # Show first 5
                    name = model.get('name', 'Unknown')
                    version = model.get('version', '?')
                    print(f"  • {name} (v{version})")
                if len(models) > 5:
                    print(f"  ... and {len(models) - 5} more models")
            
            input(f"\n{Colors.BLUE}Press Enter to continue...{Colors.END}")
            
        except Exception as e:
            print(f"{Colors.RED}Error: {e}{Colors.END}")
            print(f"{Colors.YELLOW}Continuing with demo...{Colors.END}")
            input(f"\n{Colors.BLUE}Press Enter to continue...{Colors.END}")
    
    def demo_get_single(self):
        """Demo 2: Single GET request (traditional polling)"""
        self.print_header("DEMO 2: Traditional GET Request (Like SNMP)")
        
        self.print_step(3, "Sending GET request for interface counters...")
        
        path = '/interfaces/interface[name=Ethernet1]/state/counters'
        
        print(f"\n{Colors.YELLOW}Path:{Colors.END} {path}")
        print(f"{Colors.YELLOW}This is ONE snapshot in time...{Colors.END}\n")
        
        try:
            # Use correct PyGNMI API
            result = self.client.get(path=[path], encoding='json_ietf')
            
            # Parse and display
            if result and 'notification' in result:
                for notif in result['notification']:
                    for update in notif.get('update', []):
                        value = update.get('val')
                        if isinstance(value, dict):
                            print(f"{Colors.GREEN}Interface Ethernet1 Counters:{Colors.END}")
                            print(f"  RX Bytes:   {value.get('in-octets', 0):,}")
                            print(f"  TX Bytes:   {value.get('out-octets', 0):,}")
                            print(f"  RX Packets: {value.get('in-unicast-pkts', 0):,}")
                            print(f"  TX Packets: {value.get('out-unicast-pkts', 0):,}")
                            errors = value.get('in-errors', 0) + value.get('out-errors', 0)
                            print(f"  Errors:     {errors}")
            
            print(f"\n{Colors.YELLOW}⏱️  To monitor continuously, we'd need to poll every N seconds{Colors.END}")
            print(f"{Colors.YELLOW}   (wasting resources when nothing changes!){Colors.END}")
            
            input(f"\n{Colors.BLUE}Press Enter to see the better way...{Colors.END}")
            
        except Exception as e:
            print(f"{Colors.RED}Error: {e}{Colors.END}")
            print(f"{Colors.YELLOW}This might happen if the interface doesn't exist yet.{Colors.END}")
            input(f"\n{Colors.BLUE}Press Enter to continue...{Colors.END}")
    
    def demo_subscribe_sample(self):
        """Demo 3: SAMPLE mode subscription (time-based)"""
        self.print_header("DEMO 3: Streaming Telemetry - SAMPLE Mode")
        
        print(f"{Colors.YELLOW}SAMPLE mode: Device sends data every N seconds{Colors.END}")
        print(f"{Colors.YELLOW}(Good for regular monitoring){Colors.END}\n")
        
        self.print_step(4, "Creating subscription for all interfaces...")
        
        paths = [
            '/interfaces/interface[name=*]/state/counters/in-octets',
            '/interfaces/interface[name=*]/state/counters/out-octets',
        ]
        
        print(f"\n{Colors.GREEN}Subscribing to:{Colors.END}")
        for p in paths:
            print(f"  • {p}")
        
        print(f"\n{Colors.YELLOW}Sample interval: 5 seconds{Colors.END}")
        print(f"{Colors.YELLOW}Duration: 30 seconds (or Ctrl+C to stop){Colors.END}\n")
        print(f"{Colors.CYAN}{'─'*70}{Colors.END}")
        
        try:
            # Correct PyGNMI 0.8.15 API for subscribe
            subscription = {
                'subscription': [
                    {
                        'path': path,
                        'mode': 'sample',
                        'sample_interval': 5000000000  # 5 seconds in nanoseconds
                    }
                    for path in paths
                ],
                'mode': 'stream',
                'encoding': 'json_ietf'
            }
            
            update_count = 0
            start_time = time.time()
            
            # Use subscribe2 generator
            for response in self.client.subscribe2(subscription):
                update_count += 1
                timestamp = datetime.now().strftime("%H:%M:%S")
                
                print(f"\n{Colors.BOLD}[{timestamp}] Update #{update_count}{Colors.END}")
                
                if 'update' in response:
                    notif = response['update']
                    for update in notif.get('update', []):
                        path = update.get('path', '')
                        value = update.get('val', 0)
                        
                        # Extract interface name from path
                        path_str = str(path)
                        if 'name=' in path_str or '[name=' in path_str:
                            # Try to extract interface name
                            try:
                                if 'name=' in path_str:
                                    iface = path_str.split('name=')[1].split(']')[0].split(',')[0].strip("'\"")
                                else:
                                    iface = "Unknown"
                            except:
                                iface = "Interface"
                            
                            if 'in-octets' in path_str:
                                mbps = (value * 8) / 1_000_000 if isinstance(value, (int, float)) else 0
                                print(f"  {Colors.GREEN}↓{Colors.END} {iface:12} RX: {mbps:8.2f} Mbps  ({value:,} bytes)")
                            elif 'out-octets' in path_str:
                                mbps = (value * 8) / 1_000_000 if isinstance(value, (int, float)) else 0
                                print(f"  {Colors.BLUE}↑{Colors.END} {iface:12} TX: {mbps:8.2f} Mbps  ({value:,} bytes)")
                
                # Stop after 30 seconds
                if time.time() - start_time > 30:
                    break
            
            print(f"\n{Colors.GREEN}✓ Received {update_count} updates in 30 seconds{Colors.END}")
            input(f"\n{Colors.BLUE}Press Enter to continue...{Colors.END}")
            
        except KeyboardInterrupt:
            print(f"\n{Colors.YELLOW}Stream stopped by user{Colors.END}")
            input(f"\n{Colors.BLUE}Press Enter to continue...{Colors.END}")
        except Exception as e:
            print(f"{Colors.RED}Error: {e}{Colors.END}")
            import traceback
            traceback.print_exc()
            print(f"{Colors.YELLOW}Subscription might not be supported in this mode.{Colors.END}")
            input(f"\n{Colors.BLUE}Press Enter to continue...{Colors.END}")
    
    def demo_subscribe_on_change(self):
        """Demo 4: ON_CHANGE mode subscription (event-driven)"""
        self.print_header("DEMO 4: Streaming Telemetry - ON_CHANGE Mode")
        
        print(f"{Colors.YELLOW}ON_CHANGE mode: Device sends ONLY when value changes{Colors.END}")
        print(f"{Colors.YELLOW}(Most efficient! No data when nothing happens){Colors.END}\n")
        
        self.print_step(5, "Creating ON_CHANGE subscription...")
        
        paths = [
            '/interfaces/interface[name=*]/state/oper-status',
            '/interfaces/interface[name=*]/state/admin-status',
        ]
        
        print(f"\n{Colors.GREEN}Monitoring interface status changes:{Colors.END}")
        print(f"  • Operational status (up/down)")
        print(f"  • Admin status (enabled/disabled)\n")
        
        print(f"{Colors.YELLOW}💡 In another terminal, try: docker exec -it clab-pyutrecht-telemetry-demo-spine1 Cli{Colors.END}")
        print(f"{Colors.YELLOW}   Then: enable → conf t → interface ethernet 3 → shutdown{Colors.END}\n")
        
        print(f"{Colors.CYAN}{'─'*70}{Colors.END}")
        print(f"{Colors.YELLOW}Waiting for changes... (30 seconds or Ctrl+C){Colors.END}\n")
        
        try:
            # Create ON_CHANGE subscription
            subscription = {
                'subscription': [
                    {
                        'path': path,
                        'mode': 'on_change'
                    }
                    for path in paths
                ],
                'mode': 'stream',
                'encoding': 'json_ietf'
            }
            
            update_count = 0
            start_time = time.time()
            
            for response in self.client.subscribe2(subscription):
                update_count += 1
                timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
                
                print(f"\n{Colors.BOLD}{Colors.RED}🚨 CHANGE DETECTED!{Colors.END}")
                print(f"{Colors.BOLD}[{timestamp}] Update #{update_count}{Colors.END}")
                
                if 'update' in response:
                    notif = response['update']
                    for update in notif.get('update', []):
                        path = update.get('path', '')
                        value = update.get('val', '')
                        
                        path_str = str(path)
                        if 'name=' in path_str or '[name=' in path_str:
                            try:
                                if 'name=' in path_str:
                                    iface = path_str.split('name=')[1].split(']')[0].split(',')[0].strip("'\"")
                                else:
                                    iface = "Unknown"
                            except:
                                iface = "Interface"
                            
                            if 'oper-status' in path_str:
                                color = Colors.GREEN if str(value).upper() == 'UP' else Colors.RED
                                print(f"  Interface {iface}: Operational Status → {color}{value}{Colors.END}")
                            elif 'admin-status' in path_str:
                                color = Colors.GREEN if str(value).upper() == 'UP' else Colors.YELLOW
                                print(f"  Interface {iface}: Admin Status → {color}{value}{Colors.END}")
                
                if time.time() - start_time > 30:
                    break
            
            if update_count == 0:
                print(f"{Colors.YELLOW}No changes detected (network is stable!){Colors.END}")
            else:
                print(f"\n{Colors.GREEN}✓ Detected {update_count} changes{Colors.END}")
            
            input(f"\n{Colors.BLUE}Press Enter to continue...{Colors.END}")
            
        except KeyboardInterrupt:
            print(f"\n{Colors.YELLOW}Stream stopped by user{Colors.END}")
            input(f"\n{Colors.BLUE}Press Enter to continue...{Colors.END}")
        except Exception as e:
            print(f"{Colors.RED}Error: {e}{Colors.END}")
            import traceback
            traceback.print_exc()
            print(f"{Colors.YELLOW}ON_CHANGE mode might not be supported for this path.{Colors.END}")
            input(f"\n{Colors.BLUE}Press Enter to continue...{Colors.END}")
    
    def demo_comparison(self):
        """Demo 5: Side-by-side comparison"""
        self.print_header("DEMO 5: The Difference Visualized")
        
        print(f"{Colors.YELLOW}Let's compare what we just saw:{Colors.END}\n")
        
        print(f"{Colors.BOLD}Traditional SNMP Polling:{Colors.END}")
        print(f"  {Colors.RED}-{Colors.END} Poll every 30-60 seconds")
        print(f"  {Colors.RED}-{Colors.END} Get ALL data even if unchanged")
        print(f"  {Colors.RED}-{Colors.END} Miss events between polls")
        print(f"  {Colors.RED}-{Colors.END} High device CPU load")
        print(f"  {Colors.RED}-{Colors.END} Delayed alerting (30-60s lag)")
        
        print(f"\n{Colors.BOLD}Streaming Telemetry (gNMI):{Colors.END}")
        print(f"  {Colors.GREEN}-{Colors.END} Continuous real-time updates")
        print(f"  {Colors.GREEN}-{Colors.END} Only changed data (ON_CHANGE)")
        print(f"  {Colors.GREEN}-{Colors.END} Sub-second alerting possible")
        print(f"  {Colors.GREEN}-{Colors.END} Lower device CPU usage")
        print(f"  {Colors.GREEN}-{Colors.END} Structured data (JSON/Protobuf)")
        
        print(f"\n{Colors.BOLD}Example: Network with 100 devices, 1000 metrics each{Colors.END}")
        print(f"  SNMP: 100,000 polls every 60s = {Colors.RED}1,667 requests/second{Colors.END}")
        print(f"  gNMI: Subscribe once, receive only changes = {Colors.GREEN}~10-100 updates/second{Colors.END}")
        
        input(f"\n{Colors.BLUE}Press Enter to finish...{Colors.END}")
    
    def run_full_demo(self):
        """Run complete demonstration"""
        print(f"""
{Colors.BOLD}{Colors.CYAN}
╔════════════════════════════════════════════════════════════════════╗
║                                                                    ║
║  Streaming Telemetry: Real-time Network Monitoring with Python     ║
║                                                                    ║
║  PyUtrecht Meetup - Live Demo                                      ║
║  By: Maurice Stoof                                                 ║
║                                                                    ║
╚════════════════════════════════════════════════════════════════════╝
{Colors.END}
        """)
        
        if not self.connect():
            return
        
        try:
            self.demo_capabilities()
            self.demo_get_single()
            self.demo_subscribe_sample()
            self.demo_subscribe_on_change()
            self.demo_comparison()
            
            self.print_header("Demo Complete!")
            print(f"\n{Colors.GREEN}Thank you! Questions?{Colors.END}\n")
            
        except Exception as e:
            print(f"\n{Colors.RED}Demo error: {e}{Colors.END}")
            import traceback
            traceback.print_exc()
        finally:
            if self.client:
                print(f"\n{Colors.YELLOW}Closing connection...{Colors.END}")
                try:
                    self.client.close()
                except:
                    pass


def main():
    """Main entry point"""
    demo = TelemetryDemo(host='172.20.20.11', port=6030)
    demo.run_full_demo()


if __name__ == "__main__":
    print(f"\n{Colors.YELLOW}🚀 Starting Streaming Telemetry Demo...{Colors.END}\n")
    print(f"{Colors.YELLOW}Prerequisites:{Colors.END}")
    print(f"  1. Containerlab topology running: sudo clab deploy -t topology.yml")
    print(f"  2. Python packages: pip install pygnmi grpcio grpcio-tools")
    print(f"  3. Arista cEOS image imported\n")
    
    input(f"{Colors.BLUE}Press Enter when ready to start...{Colors.END}")
    
    main()