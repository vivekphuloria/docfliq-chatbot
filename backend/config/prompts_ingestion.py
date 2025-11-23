"""
System prompts for data ingestion and processing.

This file contains prompts specifically for document ingestion,
chunking, embedding, and related preprocessing tasks.
"""

# Future ingestion prompts will be added here
PPT_SLIDE_ANALYSIS_PROMPT = """
### Slide Details extraction

Analyze this PowerPoint slide image in detail and provide a comprehensive structured analysis.
Your should include the following and be a JSON as per the sample format provided:

## 1. SLIDE Headers

- Slide title (if present)
- Slide subtitle (if present)
- Component or Section Level Subheadings(if any)
- logos present on slide

## 2. SLIDE CONTENT - FULL

- Extract ALL text visible on the slide, and structure it to convey the message of the slide. Please follow the following steps.

### Step 1 - Extract Component Details

- Extract text from each component
- Extract any visual components (images, graphics, diagrams, charts etc) if available, and think of what the information conveyed by them
- Think of any information conveyed by the relative positioning and any shapes/objects between the different textual and visual components.

### Step 2 - Use Component Details to Explain Slide Content

- Use all of the exact text mentioned in the slide,
- Try to minimise any additional text not mentioned in the slide.
- Add addional text only if some infromation is conveyed in visuals, or via the relative postioning of objects
- Output the final explaination as a markdown. Mention the content of the slide, and maybe

## 3. SLIDE CONTENT - OVERVIEW

2-4 line overview about the overall contents of the slide. This should include summary of the "SLIDE CONTENT - FULL". Mention the purpose of the slide, and the key information conveyed by the slide.

## 4. VISUAL COMPONENTS INVENTORY

- Identify all non-text visual elements, for example:
    - Images/Photos
    - Charts/Graphs
    - Diagrams
    - Tables
- Do not include boxes or shapes with text. Focus on graphical content.
- Can be empty if no visual compoenent exists 
- Output a list of all elements with the following information about each elements
    - Visual Type
    - Description: Key information conveyed by visual

## 5. SLIDE STRUCTURE

Provide an overview about the slide structure.

### STEP 1: INFORMATION SEGMENTS


- Try to break the slide down into these these segments based on their position (eg, top-half, right-half, mid-right section, etc)
- Think of sections where a single type of infomation is communicated
- Split segment, not based on individual components, but on infromation hirarchy
- Analyse what is the key information communicated in that segment
- **NOTE** : Ensure the segments are ordered from left to right, from top to bottom


### STEP 2: SEGMENT DESCRIPTION

For each segment, provide the following information in a JSON format

- Info 1: Heading of the section - 2-4 words title
- Info 2: Size and position on Slide :
    - for position use terms : top, mid, bottom, left, center, right, full_width, full_height
    - eg. 50% top-full_width, 25% bottom-right, 20% mid-right, 30% top-center
- Info 3: Structure : How the information is communicated. If it is via a Ms. PowerPoint Smart art, then mention that, else describe the component with set of components used
For example
    - Chevron list
    - Textbox with Title and Bullet list
    - Set of boxes , distributed vertically , each with an icon, title, and 2-3 lines text, connected with arrow icons
- Info 4:A brief 1-2 line overview of the content in the segment


# SAMPLE OUTPUT

```json
{
    "slide_headers": {
        "slide_title": "string - main title of the slide",
        "slide_subtitle": "string - subtitle or tagline",
        "section_subheadings": [
            "string - subheading 1",
            "string - subheading 2",
            "string - subheading 3"
        ],
        "logos": [
            {
                "logo_name": "string - organization name",
                "position": "string - location on slide"
            }
        ]
    },
    "slide_content_full": "# Main Heading\n\n## Section 1\n\nText content from component 1, incorporating exact text from slide. Visual elements like arrows indicate flow from left to right.\n\n## Section 2\n\nText content from component 2. The positioning suggests a sequential relationship.\n\n### Key Points:\n- Bullet point 1 text from slide\n- Bullet point 2 text from slide\n\n## Timeline\n\nPhase 1 (Date range) → Phase 2 (Date range) → Phase 3 (Date range)\n\nThe horizontal layout with connecting elements indicates a progression over time.",
    "slide_content_overview": {
        "summary": "2-4 line description summarizing the entire slide. This explains the main purpose of the slide and synthesizes the key messages communicated through text, visuals, and layout. It provides context for what the audience should take away from this slide."
    },
    "visual_components_inventory": [
        {
            "visual_type": "string - e.g., 'Diagram', 'Chart', 'Image', 'Table'",
            "description": "string - what information this visual conveys"
        },
        {
            ...
        },
        ...
    ],
    "slide_structure": {
        "components": [
            {
                "component_title": "component 1 title",
                "size_position": "...",
                "component_structure": "...",
                "component_overview": "..."
            },
            {
                ...
            }
        ]
    }
}
```
"""