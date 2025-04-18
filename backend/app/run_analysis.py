"""
Run Analysis Script for Privacy Data Protocol

This script generates a test dataset of browser history data and performs
privacy-preserving analysis using homomorphic encryption.
"""

import os
import json
import time
from data_generator import generate_dataset, generate_small_test_dataset
from homomorphic_encryption import PrivacyPreservingComputation

def main():
    """Run the complete analysis workflow."""
    start_time = time.time()
    
    print("Privacy Data Protocol - Browser History Analysis")
    print("=" * 50)
    
    os.makedirs("data", exist_ok=True)
    
    print("\nStep 1: Generating test dataset...")
    dataset = generate_small_test_dataset(num_users=1000, events_per_user=1000)
    
    print("\nStep 2: Initializing privacy-preserving computation engine...")
    computation = PrivacyPreservingComputation("browser_history_test_dataset.json")
    
    print("\nStep 3: Running privacy-preserving analysis...")
    results = computation.run_full_analysis(sample_size=1000)
    
    print("\nStep 4: Analysis Results")
    print("-" * 50)
    print(f"Dataset: {results['dataset_info']['total_users']} users, sampled {results['dataset_info']['sampled_users']}")
    print(f"Date range: {results['dataset_info']['date_range']}")
    
    print("\nShort Video Analysis:")
    video_results = results["short_video_analysis"]
    print(f"Total visits: {video_results['total_visits']}")
    print(f"Short video visits: {video_results['short_video_visits']} ({video_results['short_video_percentage']:.2f}%)")
    print(f"Users primarily viewing short videos: {video_results['users_primarily_video']} ({video_results['users_primarily_video_percentage']:.2f}%)")
    
    print("\nE-commerce After Video Analysis:")
    ecommerce_results = results["ecommerce_after_video_analysis"]
    print(f"Short video visits: {ecommerce_results['short_video_visits']}")
    print(f"E-commerce visits after videos: {ecommerce_results['ecommerce_after_video']} ({ecommerce_results['ecommerce_after_video_percentage']:.2f}%)")
    print(f"Users with video-to-ecommerce pattern: {ecommerce_results['users_with_pattern']} ({ecommerce_results['users_with_pattern_percentage']:.2f}%)")
    
    with open("analysis_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print("\nResults saved to analysis_results.json")
    
    end_time = time.time()
    print(f"\nAnalysis completed in {end_time - start_time:.2f} seconds")

if __name__ == "__main__":
    main()
