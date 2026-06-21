import pygame

pygame.mixer.init()


def clip_sound(original_sound, start_sec, end_sec):
    """Clips a pygame.mixer.Sound object and returns a new Sound object."""
    raw_data = original_sound.get_raw()

    # Each sample is 2 bytes (16-bit) multiplied by the number of channels (stereo=2, mono=1)
    # This formula calculates byte indices based on Pygame's default sound settings.
    sample_rate = pygame.mixer.get_init()[0]
    channels = pygame.mixer.get_init()[2]
    bytes_per_sample = 2 * channels

    start_byte = int(start_sec * sample_rate * bytes_per_sample)
    end_byte = int(end_sec * sample_rate * bytes_per_sample)

    # Ensure byte indices align to a whole sample boundary
    start_byte -= start_byte % bytes_per_sample
    end_byte -= end_byte % bytes_per_sample

    # Slice the raw bytestring
    clipped_data = raw_data[start_byte:end_byte]

    return pygame.mixer.Sound(buffer=clipped_data)


powerup_sound = pygame.mixer.Sound("sound/powerup.mp3")
explosion_sound = pygame.mixer.Sound("sound/explosion.mp3")
big_explosion_sound = pygame.mixer.Sound("sound/big_explosion.mp3")
diving_sound = clip_sound(pygame.mixer.Sound("sound/dive.mp3"), 0, 0.5)
dying_sound = pygame.mixer.Sound("sound/explosion_bubbles.mp3")
wave_sound = pygame.mixer.Sound("sound/wave.mp3")
sonar_sound = pygame.mixer.Sound("sound/sonar.mp3")
