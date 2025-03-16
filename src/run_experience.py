from constants import AvailableProjectileFinderMethods
from src.constants import ColorDomain
from src.experience_manager import ExperienceManager


def run_experience(config: str):
    experience_manager = ExperienceManager(configuration_file_path=config)

    # These values can be modified in the event someone works on the repository.
    # As of today (March 2025), the only available method is "FIND_CIRCLES".
    # To add a new method, please refer to the "src/projectile_finder.py" file.
    experience_manager.set_projectile_finder_method(AvailableProjectileFinderMethods.FIND_CIRCLES)

    # The method "FIND_CIRCLES" works on grayscale images.
    # In the event someone wants to use RGB images for his own method, this can be modified using the following line.
    experience_manager.set_color_domain_to_find_projectile(ColorDomain.GRAYSCALE)

    experience_manager.compute_kinematics()
    experience_manager.save_results_as_csv()
