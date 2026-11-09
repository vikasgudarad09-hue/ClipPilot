"""
ClipPilot Pro License Key Generator
Use this script to generate genuine Pro Lifetime license keys for paying customers.
Usage:
    python generate_key.py customer_email_or_name
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from core.license_manager import LicenseManager

def main():
    manager = LicenseManager("data")
    customer = sys.argv[1] if len(sys.argv) > 1 else "CUSTOMER"
    key = manager.generate_license_key(customer)
    
    print("\n" + "="*50)
    print("   [+] CLIPPILOT PRO - LICENSE KEY GENERATOR")
    print("="*50)
    print(f" Customer / Order ID : {customer}")
    print(f" License Key         : {key}")
    print(f" Tier                : Pro Lifetime (Unlimited Bulk & SEO)")
    print("="*50)
    print("\nSend this key to your customer. They enter it in ClipPilot to unlock Pro!\n")

if __name__ == "__main__":
    main()
