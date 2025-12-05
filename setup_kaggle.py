#!/usr/bin/env python
"""
Setup script to download Kaggle Stroke Detection dataset and configure credentials.
Run this before starting the Flask app for the first time.
"""

import os
import sys
from pathlib import Path

def setup_kaggle_credentials():
    """Guide user through Kaggle API setup"""
    print("=" * 60)
    print("Kaggle API Setup")
    print("=" * 60)
    print("\nTo download the Kaggle Stroke Detection dataset, you need:")
    print("1. A Kaggle account (sign up at https://www.kaggle.com)")
    print("2. Kaggle API credentials (kaggle.json)")
    print("\nSteps:")
    print("  1. Go to https://www.kaggle.com/settings/account")
    print("  2. Click 'Create New API Token'")
    print("  3. This downloads 'kaggle.json'")
    print("  4. Place it in: ~/.kaggle/kaggle.json")
    print("  5. On Windows, that's: C:\\Users\\<YourUsername>\\.kaggle\\kaggle.json")
    print("\n" + "=" * 60)
    
    # Check if credentials exist
    kaggle_config = Path.home() / ".kaggle" / "kaggle.json"
    if kaggle_config.exists():
        print("✓ Kaggle credentials found!")
        return True
    else:
        print("⚠ Kaggle credentials not found at:")
        print(f"  {kaggle_config}")
        print("\nPlace your kaggle.json file there and try again.")
        return False


def download_dataset():
    """Download the dataset using Kaggle API"""
    print("\nDownloading Kaggle Stroke Detection dataset...")
    try:
        from kaggle.api.kaggle_api_extended import KaggleApi
        api = KaggleApi()
        api.authenticate()
        
        dataset_name = "fedesoriano/stroke-prediction-dataset"
        download_dir = os.path.join(os.path.dirname(__file__), "instance")
        os.makedirs(download_dir, exist_ok=True)
        
        print(f"Downloading: {dataset_name}")
        api.dataset_download_files(dataset_name, path=download_dir, unzip=True)
        
        # Find the CSV file
        for file in os.listdir(download_dir):
            if file.endswith('.csv') and 'stroke' in file.lower():
                src = os.path.join(download_dir, file)
                dst = os.path.join(download_dir, "healthcare-dataset-stroke-data.csv")
                if src != dst:
                    os.rename(src, dst)
                print(f"✓ Dataset downloaded and saved to: {dst}")
                return True
        
        print("✗ Could not find CSV file in downloaded data.")
        return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("Stroke Intelligence System (SIS) - Kaggle Setup")
    print("=" * 60 + "\n")
    
    # Check credentials
    if not setup_kaggle_credentials():
        print("\n⚠ Setup incomplete. Please configure Kaggle credentials first.")
        sys.exit(1)
    
    # Download dataset
    if download_dataset():
        print("\n✓ Setup complete! You can now run: python app.py")
    else:
        print("\n⚠ Dataset download failed. Continuing anyway (you can add CSV manually).")
        print("  Place healthcare-dataset-stroke-data.csv in the 'instance' folder.")
