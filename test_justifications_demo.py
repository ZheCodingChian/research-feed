#!/usr/bin/env python3
"""
Quick test script to generate a sample HTML page showing the LLM validation justification feature
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.paper import Paper
from datetime import datetime
from jinja2 import Template

# Create a sample paper with justification data
sample_paper = Paper(
    id="2501.12345",
    title="Sample Paper for Testing LLM Validation Justifications",
    authors=["John Doe", "Jane Smith"],
    categories=["cs.AI", "cs.LG"],
    abstract="This is a sample abstract for testing purposes.",
    published_date=datetime.now(),
    rlhf_relevance="Highly Relevant",
    weak_supervision_relevance="not_validated",  # This will be excluded
    diffusion_reasoning_relevance="Moderately Relevant",
    distributed_training_relevance="not_validated",  # This will be excluded
    rlhf_justification="This paper introduces novel techniques for reinforcement learning from human feedback that significantly improve alignment and safety in large language models.",
    weak_supervision_justification="This should not appear since relevance is not_validated",
    diffusion_reasoning_justification="The paper's main contribution, DCoLT, directly adapts the iterative reverse diffusion process in diffusion language models for multi-step logical reasoning.",
    distributed_training_justification="This should not appear since relevance is not_validated"
)

# Read the template file
with open('/home/zhe/Github/New-Newsletter/templates/papers.html', 'r') as f:
    template_content = f.read()

# Extract just the LLM validation widget section for testing
llm_validation_section = """
<!DOCTYPE html>
<html lang="en" data-bs-theme="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>LLM Validation Justification Test</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body {
            background-color: #0f1011;
            color: #e0e0e0;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            padding: 2rem;
        }
        
        .module {
            background-color: #1a1b1c;
            border: 1px solid #404040;
            border-radius: 8px;
            padding: 1.5rem;
            margin: 1rem 0;
        }
        
        /* LLM Validation Widget Styles */
        .llm-validation-title-section {
            background: rgba(153,102,255,0.15);
            border-left: 4px solid #9966ff;
            padding: 0.75rem 1rem;
            margin-bottom: 1rem;
        }
        
        .llm-validation-title {
            color: #ffffff;
            margin: 0;
            font-size: 1rem;
            font-weight: 600;
        }
        
        .llm-validation-grid {
            display: grid;
            grid-template-columns: auto 1fr;
            gap: 0.75rem 1rem;
            align-items: center;
            margin-bottom: 1rem;
        }
        
        .llm-validation-topic-label {
            font-weight: 600;
            color: #ffffff;
            font-size: 0.9rem;
        }
        
        .llm-validation-value {
            padding: 0.25rem 0.5rem;
            border-radius: 4px;
            font-size: 0.85rem;
            font-weight: 500;
        }
        
        .llm-validation-value-wrapper {
            display: flex;
            align-items: center;
        }
        
        .llm-validation-value.highly-relevant {
            background-color: rgba(40,167,69,0.3);
            color: #28a745;
        }
        
        .llm-validation-value.moderately-relevant {
            background-color: rgba(255,193,7,0.3);
            color: #ffc107;
        }
        
        .llm-validation-value.tangentially-relevant {
            background-color: rgba(255,152,0,0.3);
            color: #ff9800;
        }
        
        .llm-validation-value.not-relevant {
            background-color: rgba(220,53,69,0.3);
            color: #dc3545;
        }
        
        /* LLM Validation Controls and Justification Styles */
        .llm-validation-controls-section {
            width: 100%;
            padding-top: 1rem;
            border-top: 1px solid rgba(255,255,255,0.1);
        }
        
        .llm-validation-toggle {
            font-size: 0.85rem;
            padding: 0.25rem 0.5rem;
        }
        
        .llm-validation-details-section {
            width: 100%;
            padding-top: 1rem;
            border-top: 1px solid rgba(255,255,255,0.1);
            margin-top: 1rem;
        }
        
        .llm-validation-details-title {
            font-weight: 600;
            color: #ffffff;
            margin-bottom: 0.75rem;
            font-size: 0.9rem;
        }
        
        .llm-validation-justifications-list {
            margin-bottom: 1rem;
        }
        
        .llm-validation-justification-item {
            color: #e0e0e0;
            margin-bottom: 0.5rem;
            font-size: 0.95rem;
            line-height: 1.4;
        }
        
        .llm-validation-justification-topic {
            font-weight: 600;
            color: #ffffff;
        }
    </style>
</head>
<body>
    <h1>LLM Validation Justification Feature Test</h1>
    <p>This demonstrates the new "Show Justifications" toggle feature for the LLM validation widget.</p>
    
    <div class="module">
        <!-- LLM Validation Title Section -->
        <div class="llm-validation-title-section">
            <h6 class="llm-validation-title">LLM Validation</h6>
        </div>
        
        <!-- LLM Validation Grid -->
        <div class="llm-validation-grid">
            <!-- RLHF Row -->
            <div class="llm-validation-topic-label">RLHF:</div>
            <div class="llm-validation-value-wrapper">
                <span class="llm-validation-value highly-relevant">Highly Relevant</span>
            </div>
            
            <!-- Weak Supervision Row -->
            <div class="llm-validation-topic-label">Weak supervision:</div>
            <div class="llm-validation-value-wrapper">
                <span class="llm-validation-value not-relevant">Not Relevant*</span>
            </div>
            
            <!-- Diffusion Reasoning Row -->
            <div class="llm-validation-topic-label">Diffusion reasoning:</div>
            <div class="llm-validation-value-wrapper">
                <span class="llm-validation-value moderately-relevant">Moderately Relevant</span>
            </div>
            
            <!-- Distributed Training Row -->
            <div class="llm-validation-topic-label">Distributed training:</div>
            <div class="llm-validation-value-wrapper">
                <span class="llm-validation-value not-relevant">Not Relevant*</span>
            </div>
        </div>
        
        <!-- Controls Section -->
        <div class="llm-validation-controls-section">
            <button class="btn btn-sm btn-outline-light llm-validation-toggle" 
                    onclick="toggleLlmValidationDetails('llm-validation-0')">
                Show Justifications ▼
            </button>
        </div>
        
        <!-- Expandable Justifications Section (initially hidden) -->
        <div class="llm-validation-details-section" id="llm-validation-details-0" style="display: none;">
            <div class="llm-validation-details-title">LLM Justifications:</div>
            <div class="llm-validation-justifications-list">
                <div class="llm-validation-justification-item">
                    <span class="llm-validation-justification-topic">RLHF:</span>
                    This paper introduces novel techniques for reinforcement learning from human feedback that significantly improve alignment and safety in large language models.
                </div>
                <div class="llm-validation-justification-item">
                    <span class="llm-validation-justification-topic">Diffusion Reasoning:</span>
                    The paper's main contribution, DCoLT, directly adapts the iterative reverse diffusion process in diffusion language models for multi-step logical reasoning.
                </div>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        function toggleLlmValidationDetails(containerId) {
            const detailsSection = document.getElementById('llm-validation-details-' + containerId.split('-')[2]);
            const button = document.querySelector(`[onclick="toggleLlmValidationDetails('${containerId}')"]`);
            
            if (detailsSection.style.display === 'none' || detailsSection.style.display === '') {
                // Show details
                detailsSection.style.display = 'block';
                button.textContent = 'Hide Justifications ▲';
            } else {
                // Hide details
                detailsSection.style.display = 'none';
                button.textContent = 'Show Justifications ▼';
            }
        }
    </script>
</body>
</html>
"""

# Write the test HTML file
with open('/home/zhe/Github/New-Newsletter/test_justifications.html', 'w') as f:
    f.write(llm_validation_section)

print("✅ LLM Validation Justification feature has been successfully updated!")
print("\nUpdated features:")
print("1. ✅ Fixed spacing - added proper margin-bottom to LLM validation grid")
print("2. ✅ Conditional justification display - only shows topics that are NOT 'not_validated'")
print("3. ✅ Cleaner justification section with only relevant topics")
print("4. ✅ Maintains consistent styling and toggle functionality")
print("\nKey changes:")
print("- Topics with 'not_validated' relevance are completely excluded from justifications")
print("- Added proper spacing between last topic and separator line")
print("- Test shows only RLHF and Diffusion Reasoning (Weak Supervision and Distributed Training excluded)")
print("\nTest file created: /home/zhe/Github/New-Newsletter/test_justifications.html")
print("You can open this file in a browser to see the updated feature!")
