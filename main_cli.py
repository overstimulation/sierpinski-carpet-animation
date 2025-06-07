import matplotlib.animation as animation
import matplotlib.pyplot as plt
import numpy as np

# Author: overstimulation
# Repo: https://github.com/overstimulation/sierpinski-carpet-animation


def create_sierpinski_carpet(order, size=243):
    """
    Generate a Sierpiński carpet of the given order.

    Parameters:
    - order: The recursion depth (0 = solid square, 1 = first iteration, etc.)
    - size: The size of the resulting square array (should be 3^n for some n)

    Returns:
    - A numpy array representing the carpet (1 = filled, 0 = empty)
    """
    # Initialise with a filled square
    carpet = np.ones((size, size), dtype=int)

    # Return early for order 0
    if order == 0:
        return carpet

    for i in range(size):
        for j in range(size):
            # For each pixel, check if it's in a "hole" at any level
            x, y = i, j
            for _ in range(order):
                # If we're in the middle third of the current square, it's a hole
                if (x % 3 == 1) and (y % 3 == 1):
                    carpet[i, j] = 0
                    break

                # Prepare for next iteration by dividing coordinates by 3
                x //= 3
                y //= 3

    return carpet


def create_sierpinski_animation(
    max_order=6,
    frames_per_order=15,
    size=729,
    cmap="binary",
    output_filename="sierpinski_carpet_animation",
    as_mp4=True,
    fps=10,
    progress_callback=None,
    preview_callback=None,
    phase_callback=None,  # <-- add phase_callback
):
    """
    Creates and saves an animation of the Sierpiński carpet evolution.
    Optionally calls progress_callback(percent:int), preview_callback(np.ndarray), and phase_callback(str) for GUI updates.
    """
    # Total number of frames
    total_frames = max_order * frames_per_order + frames_per_order

    # Set up the figure and axes
    fig = plt.figure(figsize=(8, 8))
    ax = plt.axes()
    ax.set_xticks([], [])
    ax.set_yticks([], [])
    fig.subplots_adjust(left=0, right=1, top=1, bottom=0)

    # Create an initial empty image plot with a defined color range
    img = ax.imshow(np.ones((size, size)), cmap=cmap, interpolation="nearest", animated=True, vmin=0, vmax=1)

    # Print information about carpet generation
    print("Generating Sierpiński carpets...")
    if phase_callback:
        phase_callback("Generating carpets...")

    # Precompute all carpet orders
    carpets = []
    for order in range(max_order + 1):
        print(f"  Generating order {order}...")
        carpet = create_sierpinski_carpet(order, size)
        carpets.append(carpet)
        # Progress for carpet generation (0-30%)
        if progress_callback:
            progress_callback(int(30 * (order + 1) / (max_order + 1)))
        if preview_callback:
            preview_callback(carpet)

    if phase_callback:
        phase_callback("Creating animation frames...")

    def animate(frame):
        # Calculate order and transition progress
        current_order = min(frame // frames_per_order, max_order)
        next_order = min(current_order + 1, max_order)
        blend_factor = (frame % frames_per_order) / frames_per_order

        if current_order == max_order:
            # If we've reached the max order, just show the final carpet
            carpet_frame = carpets[current_order]
        else:
            # Create a smooth transition between orders
            current_carpet = carpets[current_order]
            next_carpet = carpets[next_order]

            # Only apply transition to areas that will change
            carpet_frame = current_carpet.copy()

            # Identify changing pixels
            changing_pixels = current_carpet != next_carpet

            # Apply random dissolve effect for transition
            if blend_factor > 0:
                random_mask = np.random.random(size=(size, size)) < blend_factor
                pixels_to_change = changing_pixels & random_mask
                carpet_frame[pixels_to_change] = next_carpet[pixels_to_change]

        # Update the image data
        img.set_data(carpet_frame)

        # Progress for animation creation (30-90%)
        if progress_callback:
            progress_callback(30 + int(60 * frame / total_frames))
        if preview_callback:
            preview_callback(carpet_frame)

        return [img]

    # Create and save the animation
    print(f"Creating animation ({total_frames} frames)... This may take a while.")
    if phase_callback:
        phase_callback("Saving animation...")
    anim = animation.FuncAnimation(fig, animate, frames=total_frames, interval=1000 / fps, blit=True)

    # Save the animation
    save_error = None
    if as_mp4:
        try:
            filename = f"{output_filename}.mp4"
            Writer = animation.writers["ffmpeg"]
            writer = Writer(fps=fps, metadata=dict(artist="AI Generated"), bitrate=1800)
            anim.save(filename, writer=writer)
            print(f"Animation saved as {filename}")
        except Exception as e:
            print(f"\nError saving as MP4: {e}")
            print("Ensure ffmpeg is installed and accessible in your system's PATH.")
            print("Falling back to GIF (requires Pillow).")
            as_mp4 = False
            save_error = e

    if not as_mp4:
        try:
            filename = f"{output_filename}.gif"
            anim.save(filename, writer="pillow", fps=fps)
            print(f"Animation saved as {filename}")
        except Exception as e:
            print(f"\nError saving as GIF: {e}")
            print("Ensure Pillow is installed (pip install Pillow).")
            save_error = e

    plt.close(fig)
    if progress_callback:
        progress_callback(100)
    if phase_callback:
        phase_callback("Done")
    if save_error:
        print("\nAnimation generation completed, but saving failed.")
    else:
        print("\nAnimation generation and saving completed.")


# Main execution block
if __name__ == "__main__":
    print("Sierpiński Carpet Animation Generator by @overstimulation")
    print("Contribute or view source: https://github.com/overstimulation/sierpinski-carpet-animation\n")
    # Parameters for the animation
    MAX_ORDER = 15  # Maximum recursion depth
    FRAMES_PER_ORDER = 15  # Frames for transition between orders
    CARPET_SIZE = 2187  # Size of the carpet (3^7 = 2187)
    SAVE_AS_MP4 = True  # True for .mp4 (needs ffmpeg), False for .gif (needs Pillow)
    FRAMES_PER_SECOND = 10  # Speed of the animation
    COLORMAP = "binary"  # Black and white is clearest for this fractal
    OUTPUT_NAME = "sierpinski_carpet_animation"

    print(f"Creating Sierpiński carpet animation with size {CARPET_SIZE}x{CARPET_SIZE}, max order {MAX_ORDER}")

    # Create the animation
    create_sierpinski_animation(
        max_order=MAX_ORDER,
        frames_per_order=FRAMES_PER_ORDER,
        size=CARPET_SIZE,
        cmap=COLORMAP,
        output_filename=OUTPUT_NAME,
        as_mp4=SAVE_AS_MP4,
        fps=FRAMES_PER_SECOND,
    )
