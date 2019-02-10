import re
import logging
import os


logger = logging.getLogger()
logger.setLevel(logging.INFO)

def get_target_obj_name(original_obj_name):
    (base, ext) = os.path.splitext(original_obj_name)
    base = base + "_processed"
    target_obj_name = base +  ext
    return target_obj_name
