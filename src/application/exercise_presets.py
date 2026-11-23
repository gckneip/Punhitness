from dataclasses import dataclass
from typing import Optional
from src.domain.entities.exercise import MuscleGroup


@dataclass
class ExercisePreset:
    name: str
    muscle_group: MuscleGroup
    equipment: Optional[str] = None


DEFAULT_EXERCISES = [
    # Chest
    ExercisePreset("Bench Press", MuscleGroup.CHEST, "Barbell"),
    ExercisePreset("Incline Bench Press", MuscleGroup.CHEST, "Barbell"),
    ExercisePreset("Dumbbell Fly", MuscleGroup.CHEST, "Dumbbell"),
    ExercisePreset("Push-Up", MuscleGroup.CHEST, "Bodyweight"),
    ExercisePreset("Chest Dip", MuscleGroup.CHEST, "Bodyweight"),
    ExercisePreset("Cable Crossover", MuscleGroup.CHEST, "Cable"),

    # Lats
    ExercisePreset("Pull-Up", MuscleGroup.LATS, "Bodyweight"),
    ExercisePreset("Lat Pulldown", MuscleGroup.LATS, "Cable"),
    ExercisePreset("Barbell Row", MuscleGroup.LATS, "Barbell"),
    ExercisePreset("Seated Cable Row", MuscleGroup.LATS, "Cable"),
    ExercisePreset("T-Bar Row", MuscleGroup.LATS, "Barbell"),

    # Traps
    ExercisePreset("Barbell Shrug", MuscleGroup.TRAPS, "Barbell"),

    # Lower Back
    ExercisePreset("Deadlift", MuscleGroup.LOWER_BACK, "Barbell"),

    # Quads
    ExercisePreset("Squat", MuscleGroup.QUADS, "Barbell"),
    ExercisePreset("Leg Press", MuscleGroup.QUADS, "Machine"),
    ExercisePreset("Walking Lunge", MuscleGroup.QUADS, "Dumbbell"),
    ExercisePreset("Leg Extension", MuscleGroup.QUADS, "Machine"),

    # Hamstrings
    ExercisePreset("Leg Curl", MuscleGroup.HAMSTRINGS, "Machine"),
    ExercisePreset("Romanian Deadlift", MuscleGroup.HAMSTRINGS, "Barbell"),

    # Glutes
    ExercisePreset("Hip Thrust", MuscleGroup.GLUTES, "Barbell"),

    # Calves
    ExercisePreset("Calf Raise", MuscleGroup.CALVES, "Machine"),

    # Front Delts
    ExercisePreset("Overhead Press", MuscleGroup.FRONT_DELTS, "Barbell"),
    ExercisePreset("Front Raise", MuscleGroup.FRONT_DELTS, "Dumbbell"),
    ExercisePreset("Arnold Press", MuscleGroup.FRONT_DELTS, "Dumbbell"),

    # Side Delts
    ExercisePreset("Lateral Raise", MuscleGroup.SIDE_DELTS, "Dumbbell"),
    ExercisePreset("Upright Row", MuscleGroup.SIDE_DELTS, "Barbell"),

    # Rear Delts
    ExercisePreset("Face Pull", MuscleGroup.REAR_DELTS, "Cable"),
    ExercisePreset("Reverse Fly", MuscleGroup.REAR_DELTS, "Dumbbell"),

    # Biceps
    ExercisePreset("Barbell Curl", MuscleGroup.BICEPS, "Barbell"),
    ExercisePreset("Dumbbell Curl", MuscleGroup.BICEPS, "Dumbbell"),
    ExercisePreset("Hammer Curl", MuscleGroup.BICEPS, "Dumbbell"),

    # Triceps
    ExercisePreset("Tricep Pushdown", MuscleGroup.TRICEPS, "Cable"),
    ExercisePreset("Skull Crusher", MuscleGroup.TRICEPS, "Barbell"),
    ExercisePreset("Close-Grip Bench Press", MuscleGroup.TRICEPS, "Barbell"),

    # Forearms
    ExercisePreset("Wrist Curl", MuscleGroup.FOREARMS, "Dumbbell"),

    # Abs
    ExercisePreset("Plank", MuscleGroup.ABS, "Bodyweight"),
    ExercisePreset("Crunch", MuscleGroup.ABS, "Bodyweight"),
    ExercisePreset("Hanging Leg Raise", MuscleGroup.ABS, "Bodyweight"),
    ExercisePreset("Ab Wheel Rollout", MuscleGroup.ABS, "Ab Wheel"),
    ExercisePreset("Sit-Up", MuscleGroup.ABS, "Bodyweight"),

    # Obliques
    ExercisePreset("Russian Twist", MuscleGroup.OBLIQUES, "Bodyweight"),
    ExercisePreset("Side Plank", MuscleGroup.OBLIQUES, "Bodyweight"),

    # Cardio
    ExercisePreset("Running", MuscleGroup.CARDIO),
    ExercisePreset("Cycling", MuscleGroup.CARDIO, "Bike"),
    ExercisePreset("Rowing", MuscleGroup.CARDIO, "Rowing Machine"),
    ExercisePreset("Jump Rope", MuscleGroup.CARDIO, "Jump Rope"),
    ExercisePreset("Stair Climber", MuscleGroup.CARDIO, "Machine"),

    # Full Body
    ExercisePreset("Burpee", MuscleGroup.FULL_BODY, "Bodyweight"),
    ExercisePreset("Kettlebell Swing", MuscleGroup.FULL_BODY, "Kettlebell"),
    ExercisePreset("Clean and Jerk", MuscleGroup.FULL_BODY, "Barbell"),
    ExercisePreset("Thruster", MuscleGroup.FULL_BODY, "Barbell"),
]
