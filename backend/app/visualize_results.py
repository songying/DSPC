"""
Visualization Script for Privacy Data Protocol Analysis Results

This script creates visualizations of the privacy-preserving analysis results
to better understand user behavior patterns.
"""

import json
import os
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import LinearSegmentedColormap

def load_results(file_path="analysis_results.json"):
    """Load analysis results from JSON file."""
    with open(file_path, 'r') as f:
        return json.load(f)

def create_visualizations(results, output_dir="visualizations"):
    """Create visualizations from analysis results."""
    os.makedirs(output_dir, exist_ok=True)
    
    video_results = results["short_video_analysis"]
    ecommerce_results = results["ecommerce_after_video_analysis"]
    dataset_info = results["dataset_info"]
    
    plt.figure(figsize=(12, 8))
    
    plt.subplot(1, 2, 1)
    labels = ['Short Video Content', 'Other Content']
    sizes = [video_results['short_video_percentage'], 100 - video_results['short_video_percentage']]
    colors = ['#6366F1', '#E5E7EB']
    explode = (0.1, 0)
    
    plt.pie(sizes, explode=explode, labels=labels, colors=colors, autopct='%1.1f%%',
            shadow=True, startangle=140)
    plt.axis('equal')
    plt.title('Content Viewing Distribution', fontsize=14)
    
    plt.subplot(1, 2, 2)
    categories = ['Primarily Short Videos', 'Other Content Preference']
    values = [video_results['users_primarily_video_percentage'], 
              100 - video_results['users_primarily_video_percentage']]
    
    bars = plt.bar(categories, values, color=['#6366F1', '#E5E7EB'])
    plt.ylabel('Percentage of Users')
    plt.title('User Content Preferences', fontsize=14)
    plt.ylim(0, 100)
    
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height + 1,
                 f'{height:.1f}%', ha='center', va='bottom')
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'short_video_behavior.png'), dpi=300)
    
    plt.figure(figsize=(12, 8))
    
    plt.subplot(1, 2, 1)
    labels = ['Visit E-commerce After Videos', 'No E-commerce After Videos']
    sizes = [ecommerce_results['ecommerce_after_video_percentage'], 
             100 - ecommerce_results['ecommerce_after_video_percentage']]
    colors = ['#10B981', '#E5E7EB']
    explode = (0.1, 0)
    
    plt.pie(sizes, explode=explode, labels=labels, colors=colors, autopct='%1.1f%%',
            shadow=True, startangle=140)
    plt.axis('equal')
    plt.title('E-commerce Visits After Short Videos', fontsize=14)
    
    plt.subplot(1, 2, 2)
    categories = ['Have Video→E-commerce Pattern', 'No Video→E-commerce Pattern']
    values = [ecommerce_results['users_with_pattern_percentage'], 
              100 - ecommerce_results['users_with_pattern_percentage']]
    
    bars = plt.bar(categories, values, color=['#10B981', '#E5E7EB'])
    plt.ylabel('Percentage of Users')
    plt.title('Users with Video→E-commerce Behavior Pattern', fontsize=14)
    plt.ylim(0, 100)
    
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height + 1,
                 f'{height:.1f}%', ha='center', va='bottom')
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'ecommerce_after_video_behavior.png'), dpi=300)
    
    plt.figure(figsize=(14, 8))
    
    total_users = 100
    short_video_users = video_results['users_primarily_video_percentage']
    ecommerce_after_video_users = ecommerce_results['users_with_pattern_percentage']
    
    colors = ['#6366F1', '#10B981', '#F59E0B']
    n_bins = 100
    cmap_name = 'custom_diverging'
    cm = LinearSegmentedColormap.from_list(cmap_name, colors, N=n_bins)
    
    plt.subplot(1, 1, 1)
    
    plt.fill_between([0, 1], [0, 0], [total_users, total_users], color='#E5E7EB', alpha=0.3)
    plt.fill_between([1, 2], [0, 0], [short_video_users, short_video_users], color='#6366F1', alpha=0.7)
    plt.fill_between([2, 3], [0, 0], [ecommerce_after_video_users, ecommerce_after_video_users], color='#10B981', alpha=0.7)
    
    x = [1, 1, 2, 2]
    y1 = [0, short_video_users, short_video_users, 0]
    y2 = [short_video_users, total_users, total_users, short_video_users]
    plt.fill(x, y1, color='#6366F1', alpha=0.5)
    plt.fill(x, y2, color='#E5E7EB', alpha=0.3)
    
    x = [2, 2, 3, 3]
    y1 = [0, ecommerce_after_video_users, ecommerce_after_video_users, 0]
    y2 = [ecommerce_after_video_users, short_video_users, short_video_users, ecommerce_after_video_users]
    plt.fill(x, y1, color='#10B981', alpha=0.5)
    plt.fill(x, y2, color='#6366F1', alpha=0.3)
    
    plt.text(0.5, 50, 'All Users', ha='center', va='center', fontsize=12)
    plt.text(1.5, short_video_users/2, f'Short Video\nViewers\n{short_video_users:.1f}%', 
             ha='center', va='center', fontsize=12)
    plt.text(2.5, ecommerce_after_video_users/2, f'E-commerce After\nVideo\n{ecommerce_after_video_users:.1f}%', 
             ha='center', va='center', fontsize=12)
    
    plt.axis('off')
    plt.title('User Behavior Flow', fontsize=16)
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'user_behavior_flow.png'), dpi=300)
    
    plt.figure(figsize=(14, 10))
    
    plt.suptitle('Privacy-Preserving Browser History Analysis', fontsize=20)
    plt.figtext(0.5, 0.92, 
                f"Analysis of {dataset_info['total_users']} users with {video_results['total_visits']} browsing events",
                ha='center', fontsize=14)
    
    plt.subplot(2, 2, 1)
    plt.axis('off')
    metrics_text = (
        f"Dataset Information:\n"
        f"• Total Users: {dataset_info['total_users']:,}\n"
        f"• Sampled Users: {dataset_info['sampled_users']:,}\n"
        f"• Total Browsing Events: {video_results['total_visits']:,}\n"
        f"• Date Range: {dataset_info['date_range']}\n\n"
        f"Key Findings:\n"
        f"• {video_results['short_video_percentage']:.1f}% of all content views are short videos\n"
        f"• {video_results['users_primarily_video_percentage']:.1f}% of users primarily watch short videos\n"
        f"• {ecommerce_results['ecommerce_after_video_percentage']:.1f}% of short video views are followed by e-commerce visits\n"
        f"• {ecommerce_results['users_with_pattern_percentage']:.1f}% of users exhibit the video→e-commerce pattern"
    )
    plt.text(0.1, 0.5, metrics_text, va='center', fontsize=12, linespacing=1.5)
    
    plt.subplot(2, 2, 2)
    labels = ['Short Video Content', 'Other Content']
    sizes = [video_results['short_video_percentage'], 100 - video_results['short_video_percentage']]
    colors = ['#6366F1', '#E5E7EB']
    explode = (0.1, 0)
    
    plt.pie(sizes, explode=explode, labels=labels, colors=colors, autopct='%1.1f%%',
            shadow=True, startangle=140)
    plt.axis('equal')
    plt.title('Content Viewing Distribution', fontsize=14)
    
    plt.subplot(2, 2, 3)
    categories = ['Primarily\nShort Videos', 'Other Content\nPreference']
    values = [video_results['users_primarily_video_percentage'], 
              100 - video_results['users_primarily_video_percentage']]
    
    bars = plt.bar(categories, values, color=['#6366F1', '#E5E7EB'])
    plt.ylabel('Percentage of Users')
    plt.title('User Content Preferences', fontsize=14)
    plt.ylim(0, 100)
    
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height + 1,
                 f'{height:.1f}%', ha='center', va='bottom')
    
    plt.subplot(2, 2, 4)
    categories = ['Have\nVideo→E-commerce\nPattern', 'No\nVideo→E-commerce\nPattern']
    values = [ecommerce_results['users_with_pattern_percentage'], 
              100 - ecommerce_results['users_with_pattern_percentage']]
    
    bars = plt.bar(categories, values, color=['#10B981', '#E5E7EB'])
    plt.ylabel('Percentage of Users')
    plt.title('Users with Video→E-commerce Pattern', fontsize=14)
    plt.ylim(0, 100)
    
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height + 1,
                 f'{height:.1f}%', ha='center', va='bottom')
    
    plt.tight_layout(rect=(0, 0, 1, 0.9))
    plt.savefig(os.path.join(output_dir, 'analysis_dashboard.png'), dpi=300)
    
    print(f"Visualizations created and saved to {output_dir}/")
    return [
        os.path.join(output_dir, 'short_video_behavior.png'),
        os.path.join(output_dir, 'ecommerce_after_video_behavior.png'),
        os.path.join(output_dir, 'user_behavior_flow.png'),
        os.path.join(output_dir, 'analysis_dashboard.png')
    ]

if __name__ == "__main__":
    if not os.path.exists("analysis_results.json"):
        print("Analysis results file not found. Please run the analysis first.")
        exit(1)
    
    results = load_results()
    visualization_files = create_visualizations(results)
    
    print("Visualization complete. The following files were created:")
    for file in visualization_files:
        print(f"- {file}")
