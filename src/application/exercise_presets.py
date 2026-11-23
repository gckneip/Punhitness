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

    # Back
    ExercisePreset("Deadlift", MuscleGroup.BACK, "Barbell"),
    ExercisePreset("Pull-Up", MuscleGroup.BACK, "Bodyweight"),
    ExercisePreset("Lat Pulldown", MuscleGroup.BACK, "Cable"),
    ExercisePreset("Barbell Row", MuscleGroup.BACK, "Barbell"),
    ExercisePreset("Seated Cable Row", MuscleGroup.BACK, "Cable"),
    ExercisePreset("T-Bar Row", MuscleGroup.BACK, "Barbell"),

    # Legs
    ExercisePreset("Squat", MuscleGroup.LEGS, "Barbell"),
    ExercisePreset("Leg Press", MuscleGroup.LEGS, "Machine"),
    ExercisePreset("Walking Lunge", MuscleGroup.LEGS, "Dumbbell"),
    ExercisePreset("Leg Extension", MuscleGroup.LEGS, "Machine"),
    ExercisePreset("Leg Curl", MuscleGroup.LEGS, "Machine"),
    ExercisePreset("Romanian Deadlift", MuscleGroup.LEGS, "Barbell"),
    ExercisePreset("Calf Raise", MuscleGroup.LEGS, "Machine"),

    # Shoulders
    ExercisePreset("Overhead Press", MuscleGroup.SHOULDERS, "Barbell"),
    ExercisePreset("Lateral Raise", MuscleGroup.SHOULDERS, "Dumbbell"),
    ExercisePreset("Front Raise", MuscleGroup.SHOULDERS, "Dumbbell"),
    ExercisePreset("Arnold Press", MuscleGroup.SHOULDERS, "Dumbbell"),
    ExercisePreset("Face Pull", MuscleGroup.SHOULDERS, "Cable"),
    ExercisePreset("Barbell Shrug", MuscleGroup.SHOULDERS, "Barbell"),

    # Arms
    ExercisePreset("Barbell Curl", MuscleGroup.ARMS, "Barbell"),
    ExercisePreset("Dumbbell Curl", MuscleGroup.ARMS, "Dumbbell"),
    ExercisePreset("Hammer Curl", MuscleGroup.ARMS, "Dumbbell"),
    ExercisePreset("Tricep Pushdown", MuscleGroup.ARMS, "Cable"),
    ExercisePreset("Skull Crusher", MuscleGroup.ARMS, "Barbell"),
    ExercisePreset("Close-Grip Bench Press", MuscleGroup.ARMS, "Barbell"),

    # Core
    ExercisePreset("Plank", MuscleGroup.CORE, "Bodyweight"),
    ExercisePreset("Crunch", MuscleGroup.CORE, "Bodyweight"),
    ExercisePreset("Hanging Leg Raise", MuscleGroup.CORE, "Bodyweight"),
    ExercisePreset("Russian Twist", MuscleGroup.CORE, "Bodyweight"),
    ExercisePreset("Ab Wheel Rollout", MuscleGroup.CORE, "Ab Wheel"),
    ExercisePreset("Sit-Up", MuscleGroup.CORE, "Bodyweight"),

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
