# Visualizer
- Palm Bounding Box (4 Metacarpal point (Index, Middle, Ring, Pinky) + 1 Wrist point) with side details (TOP, BOTTOM, LEFT, RIGHT)
- Joint Bounding Box (each of the 4 Proximal Phalanges point (Index, Middle, Ring, Pinky))
- Fingertip ROI (5 Fingertip points (Index, Middle, Ring, Pinky, Thumb))
- 3-axis ROI (fingertip of Middle Finger (X-axis), Index Finger (Y-axis), and Thumb (Z-axis))
- Wrist anchor point (Wrist point, on peace sign gesture and f sign gesture)
- Static 3-axis graph (fingertip of Middle Finger (X-axis), Index Finger (Y-axis), and Thumb (Z-axis) connected to a middle point relative to the 3 points in a straight line from fingertip to the central N-axis point)
- Tilt anchor point (middle point of Palm Bounding Box and Middle finger Proximal Phalanges point).

# gesture Validation
## Action Control
- **Palm Neutral:**
    - Trigger when the palm is in a neutral position.
    - **Valid if** all fingers are extended outward and not within the Palm Bounding Box.
- **Attack/Tap/LMB:** 
    - Trigger once when the gesture is detected (opytional added property **Hold**, **Repeating (Optional +Interval**))
    - Requires re-engagement to trigger again.
    - **Valid if** Thumb fingertip is within the Palm Bounding Box.
- **Skill #1/Key 1/Key E:**
    - Trigger once when the gesture is detected (optional added property **Hold**, **Repeating (Optional +Interval**))
    - Requires re-engagement to trigger again.
    - **Valid if** Index fingertip is within the Joint Bounding Box and not within the Palm Bounding Box.
- **Skill #2/Key 2/Key R:**
    - Trigger once when the gesture is detected (optional added property **Hold**, **Repeating (Optional +Interval**))
    - Requires re-engagement to trigger again.
    - **Valid if** Middle fingertip is within the Joint Bounding Box and not within the Palm Bounding Box.
- **Skill #3/Key 3/Key Q:**
    - Trigger once when the gesture is detected (optional added property **Hold**, **Repeating (Optional +Interval**))
    - Requires re-engagement to trigger again.
    - **Valid if** Ring fingertip is within the Joint Bounding Box and not within the Palm Bounding Box.
- **Utility/Key 4/Key T:**
    - Trigger once when the gesture is detected (optional added property **Hold**, **Repeating (Optional +Interval**))
    - Requires re-engagement to trigger again.
    - **Valid if** Pinky fingertip is within the Joint Bounding Box and not within the Palm Bounding Box.

## Camera Control
- **Camera Neutral:**
    - Trigger when the camera is in a neutral position.
    - **Valid if** all Ring and Pinker finger curled and their fingertip is within the Palm Bounding Box.
    - **Pan Control:**
        - Pan control follows the 3 Axis formations from the 3 fingertips of the Middle Finger (X-axis), Index Finger (Y-axis), and Thumb (Z-axis).
        - Pan movement is considered **TRUE** if any of the 3 Axis line (fingertip to N-axis point) increased or decreased in length.
        - **IF** Y-axis length decreases, X-axis length increases above **Palmm Bounding Box - TOP** side, and Z-axis length remains the same, then it is considered a **Pan Up** movement.
        - **IF** Y-axis length increases below **Palm Bounding Box - BOTTOM** side, X-axis length decreases, and Z-axis length remains the same, then it is considered a **Pan Down** movement.
        - **IF** Y-axis length remains the same, X-axis length increases above **Palm Bounding Box - LEFT** side, and Z-axis length decreases, then it is considered a **Pan Left** movement.
        - **IF** Y-axis length remains the same, X-axis length decreases, Z-axis length increases above **Palm Bounding Box - RIGHT** side, then it is considered a **Pan Right** movement.
        - **IF** the 3 axis graph formation is broken, and instead 3 axis tip points ROI are adjacent to each other with the 3 axis finger extended all to the **Palm Bounding Box - LEFT** side, the it is considered a **Mouse Middle Click/Camera Lock** movement.

## Movement Control
- **Movement Neutral:**
    - Trigger when the movement is in a neutral position.
    - The palm is facing the camera.
    - **Valid if** atleast Ring fingertip is within the Palm Bounding Box, and optionally all fingertips is within the Palm Bounding Box forming a fist.
- **Movement Forward/W:**
    - Trigger when the hand moves closer to the camera, and the Palm Bounding Box is getting bigger than it's neutral position.
    - **Valid if** the Rign fingertip is within the Palm Bounding Box, and optionally all fingertips is within the Palm Bounding Box forming a fist.
- **Movement Backward/S:**
    - Trigger when the hand moves away from the camera, and the Palm Bounding Box is getting smaller than its neutral position.
    - **Valid if** the Ring fingertip is within the Palm Bounding Box, and optionally all fingertips is within the Palm Bounding Box forming a fist.
- **Movement Left/A:**
    - Trigger when the Thumb fingertip extended outward and not within the Palm Bounding Box.
    - **Validd if** the Thumb fingertip is not within the Palm Bounding Box, and optionally all fingertips is within the Palm Bounding Box.
- **Movement Right/D:**
    - Trigger when the Pinky fingertip extended outward and not within the Palm Bounding Box.
    - **Valid if** the Pinky fingertip is not within the Palm Bounding Box, and optionally all fingertips is within the Palm Bounding Box.
- **Shift/Sprint/Crouch:**
    - Trigger when the Index finger is raised while curled, and not within the Palm Bounding Box (optional added property **Hold**, **Repeating (Optional +Interval**)) and optionally other fingers are curled and within the Palm Bounding Box.
    - **Valid if** the Index finger Middle Phalanges is within the Joint Bounding Box, and not within the Palm Bounding Box.
- **Jump/Space:**
    - Trigger once when the Pinky and Thumb fingertip are extended outward and not within the Palm Bounding Box, and the palm is tilted backwards (optional added property **Hold**, **Repeating (Optional +Interval**)) and optionally other fingers are curled and within the Palm Bounding Box.
    - **Valid if** both Pinky and Thumb fingertip (neutral Movement Left/Right) are not within the Palm Bounding Box, Tilt anchor point line is decreasing inwards from the center of the Palm Bounding Box.

## Navigation Control
- **Navigation Neutral:**
    - Trigger when the navigation is in a neutral position.
    - **Valid if** all fingertips are extended outward and not within the Palm Bounding Box.
- **Peace Sign/OK/Confirmation/Enter:**
    - Trigger once when a peace sign gesture is detected, with Index finger and Middle finger extended outward and spaced apart with other fingers curled and within the Palm Bounding Box (optional added property **Hold**, **Repeating (Optional +Interval**)).
    - **Valid of** Index and Middle fingertip are extended outward and not within the Palm Bounding Box.
- **F Sign/Tilted Peace Sign/Interact/key F:**
    - Trigger once when a tilted peace sign gesture is detected, with Index finger and Middle finger extended outward and spaced apart and are tilted to side with other fingers curled and within the Palm Bounding Box (optional added property **Hold**, **Repeating (Optional +Interval**)).
    - **Valid if** Index and Middle fingertip are extended outward and not within the Palm Bounding Box, the wrist to anchor point line is extended away from the initial point, and both Index and Middle fingertip are in either to the Left or Right side of the Palm Bounding Box.
- **Thumbs Down/Cancel/ESC:**
    - Trigger once when a thumbs down gesture is detected, with Thumb fingertip extended downward and other fingers curled and within the Palm Bounding Box (optional added property **Hold**, **Repeating (Optional +Interval**)).
    - **Valid if** Thumb fingertip is extended downward and not within the Palm Bounding Box, while also positioned below the Palm Bounding Box - BOTTOM side.

# Project Structure

The project is organized into the following main components:

- **`hand_control.py`**: The main entry point for the application. It initializes the hand tracking, loads the configuration, and manages the gesture recognition loop.
- **`comp_CentralLinker.py`**: A central component that links the different control modules (Action, Camera, Movement, Navigation) and dispatches the recognized gestures to the appropriate handlers.
- **`visualizer.py`**: A module for visualizing the hand landmarks, bounding boxes, and other debug information.
- **`validator.py`**: A centralized module for all configuration and data validation.
- **`CONFIG/`**: A directory containing all the configuration files for the application.
    - **`AxisConfig/`**: Configuration for the camera control axes.
    - **`GestureDefinition/`**: Definitions of the gestures and their validation criteria.
    - **`HandConfig/`**: Configuration for the hand tracking and profiling.
- **`MOVEMENTS/`**: Core directory for gesture logic, organized by control type. This modular structure is preserved.
    - `ActionControl/`, `CameraControl/`, `MovementControl/`, `NavigationControl/`: Each module contains a `determinator.py` to identify the active gesture and a `gestures/` subdirectory for individual gesture logic.
- **`resBalancer/`**: A performance-critical module written in C/C++ for resource-intensive calculations.
    - **`resCalculator.py`**: A Python wrapper for the `resBalancer` library.
- **`images/`**: Contains images for documentation and visualization.

## Component Analysis

| Path | Type | Viability & Performance | Necessity & Complexity |
| :--- | :--- | :--- | :--- |
| **Root Directory Files** | | | |
| `.gitignore` | File | **Viable & No Impact**: Standard for version control. | **Necessary**: Prevents unwanted files from being tracked by Git. Low complexity. |
| `comp_CentralLinker.py` | File | **Viable & High Impact**: Acts as a central dispatcher for hand data to various control modules. | **Necessary**: Crucial for modularity and routing. Its efficiency directly impacts overall system responsiveness. Medium complexity. |
| `hand_control.py` | File | **Viable & High Impact**: The main application entry point. Orchestrates hand tracking, configuration loading, and the main processing loop. | **Necessary**: Core of the application. Its design impacts overall system stability and performance. High complexity. |
| `LICENSE` | File | **Viable & No Impact**: Defines the project's licensing. | **Necessary**: Legal requirement for open-source projects. Low complexity. |
| `README.md` | File | **Viable & No Impact**: Primary project documentation. | **Necessary**: Provides an overview, setup instructions, and general information. Low complexity. |
| `requirements.txt` | File | **Viable & No Impact**: Lists Python dependencies. | **Necessary**: Ensures consistent environment setup for development and deployment. Low complexity. |
| `validator.py` | File | **Viable & Medium Impact**: Centralized module for all configuration and data validation. | **Necessary**: Ensures data integrity and consistency across the application. Consolidating validation here reduces redundancy and potential failure points. Medium complexity. |
| `visualizer.py` | File | **Viable & Medium Impact**: Handles visualization of hand landmarks, bounding boxes, and debug information. | **Necessary**: Essential for development, debugging, and potentially for user feedback. Its performance should be considered to avoid impacting the main loop. Medium complexity. |
| **`CONFIG/` Directory** | | | |
| `CONFIG/` | Directory | **Viable & No Impact**: Organizes all application configuration files. | **Necessary**: Promotes separation of concerns, making configurations easy to manage and update without code changes. Low complexity. |
| `CONFIG/AxisConfig/` | Directory | **Viable & No Impact**: Contains configuration specific to camera control axes. | **Necessary**: Allows for flexible and customizable axis behavior. Low complexity. |
| `CONFIG/AxisConfig/axisControl.jsonc` | File | **Viable & No Impact**: JSONC file for axis control settings. | **Necessary**: Stores specific parameters for axis control. Low complexity. |
| `CONFIG/AxisConfig/axisProfile.jsonc` | File | **Viable & No Impact**: JSONC file for axis profiles. | **Necessary**: Defines different profiles for axis behavior. Low complexity. |
| `CONFIG/GestureDefinition/` | Directory | **Viable & No Impact**: Contains definitions for various gestures. | **Necessary**: Centralizes gesture definitions, making them easily modifiable. Low complexity. |
| `CONFIG/GestureDefinition/definitions.jsonc` | File | **Viable & No Impact**: JSONC file containing gesture definitions. | **Necessary**: Stores the detailed definitions and criteria for each gesture. Low complexity. |
| `CONFIG/HandConfig/` | Directory | **Viable & No Impact**: Contains configuration for hand tracking and profiling. | **Necessary**: Allows for customization of hand tracking parameters. Low complexity. |
| `CONFIG/HandConfig/hand_profile.jsonc` | File | **Viable & No Impact**: JSONC file for hand profiles. | **Necessary**: Defines different profiles for hand tracking. Low complexity. |
| `CONFIG/README.md` | File | **Viable & No Impact**: Documentation for the CONFIG directory. | **Recommended**: Provides context for the configuration files. Low complexity. |
| **`images/` Directory** | | | |
| `images/` | Directory | **Viable & No Impact**: Stores images used for documentation or visual aids. | **Recommended**: Useful for visual explanations in documentation. Low complexity. |
| `images/*.jpg` | Files | **Viable & No Impact**: Image files. | **Recommended**: Visual assets for documentation. Low complexity. |
| `images/README.md` | File | **Viable & No Impact**: Documentation for the images directory. | **Recommended**: Provides context for the images. Low complexity. |
| **`MOVEMENTS/` Directory** | | | |
| `MOVEMENTS/` | Directory | **Viable & High Impact**: Contains the core logic for gesture recognition, organized by control type. | **Necessary**: This modular structure is excellent for managing different types of gesture controls. Performance is critical here. High complexity. |
| `MOVEMENTS/*/determinator.py` | File | **Viable & High Impact**: Each `determinator.py` is responsible for identifying the active gesture within its specific control domain (Action, Camera, etc.). | **Necessary**: These are critical for real-time gesture recognition. Their efficiency directly impacts responsiveness. Potential performance bottleneck if not optimized. High complexity. |
| `MOVEMENTS/*/gestures/` | Directory | **Viable & High Impact**: Contains individual Python files for each specific gesture. | **Necessary**: This highly modular approach allows for easy addition, modification, or removal of individual gestures without affecting others. Performance depends on the complexity of each gesture's logic. High complexity. |
| `MOVEMENTS/GestureSimplified.md` | File | **Viable & No Impact**: Documentation for simplified gestures. | **Necessary**: Provides a clear overview of the gesture validation logic. Low complexity. |
| **`resBalancer/` Directory** | | | |
| `resBalancer/` | Directory | **Viable & High Impact**: Contains C/C++ code for performance-critical calculations. | **Recommended**: Essential for offloading computationally intensive tasks from Python, significantly boosting performance. Introduces build system complexity. High complexity. |
| `resBalancer/cLinker.h` | File | **Viable & No Impact**: C header file for linking. | **Necessary**: Part of the C/C++ module. Low complexity. |
| `resBalancer/resBalancer.h` | File | **Viable & No Impact**: C header file for the balancer. | **Necessary**: Part of the C/C++ module. Low complexity. |
| `resBalancer/resCalculator.py` | File | **Viable & No Impact**: Python wrapper for the C/C++ module. | **Necessary**: Provides a Python interface to the C/C++ functionality. Medium complexity. |
| `resBalancer/comp/` | Directory | **Viable & No Impact**: Contains the C/C++ source files. | **Necessary**: Stores the actual C/C++ implementation. Low complexity. |
| `resBalancer/comp/accel_balancer.c` | File | **Viable & High Impact**: C source file for acceleration balancing. | **Necessary**: Core of the performance-critical module. High complexity. |
| `resBalancer/comp/accel_balancer.cpp` | File | **Viable & High Impact**: C++ source file for acceleration balancing. | **Necessary**: Core of the performance-critical module. High complexity. |