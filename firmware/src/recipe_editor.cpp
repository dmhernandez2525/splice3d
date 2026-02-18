#include "recipe_editor.h"
#include "config.h"

namespace {

struct State {
    RecipeEditorStats stats;
    bool initialized;
};

State st;

}  // namespace

void setupRecipeEditor() {
    st = {};
    st.initialized = true;
    Serial.println(F("RECIPE_EDITOR_INIT"));
}

void updateRecipeEditor() {
    if (!st.initialized) return;
}

RecipeEditorStats getRecipeEditorStats() {
    return st.stats;
}

void serializeRecipeEditorStats() {
    RecipeEditorStats s = st.stats;
    Serial.print(F("RECIPE_EDITOR_STATS"));
    Serial.print(F(" totalRecipes="));
    Serial.print(s.totalRecipes);
    Serial.print(F(" activeRecipe="));
    Serial.print(s.activeRecipe);
    Serial.print(F(" totalSegments="));
    Serial.print(s.totalSegments);
    Serial.print(F(" lastEditTimestamp="));
    Serial.print(s.lastEditTimestamp);
    Serial.print(F(" validationErrors="));
    Serial.print(s.validationErrors);
    Serial.println();
}
