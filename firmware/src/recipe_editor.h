/**
 * Splice3D Recipe Editor For Visual Splice Creation (F8.1).
 *
 * Visual recipe creation interface with segment lists, material assignments, and validation.
 */

#ifndef RECIPE_EDITOR_H
#define RECIPE_EDITOR_H

#include <Arduino.h>

struct RecipeEditorStats {
    uint32_t totalRecipes;
    uint16_t activeRecipe;
    uint32_t totalSegments;
    uint32_t lastEditTimestamp;
    uint16_t validationErrors;
};

void setupRecipeEditor();
void updateRecipeEditor();
RecipeEditorStats getRecipeEditorStats();
void serializeRecipeEditorStats();

#endif  // RECIPE_EDITOR_H
