package be.hershalpandya.appforkids;

import android.app.Activity;
import android.app.AlertDialog;
import android.text.InputType;
import android.widget.EditText;
import org.json.JSONArray;
import org.json.JSONObject;
import java.util.Locale;
import java.util.UUID;
import android.content.res.ColorStateList;
import android.graphics.Color;
import android.graphics.Insets;
import android.graphics.Typeface;
import android.graphics.drawable.GradientDrawable;
import android.graphics.drawable.RippleDrawable;
import android.graphics.drawable.StateListDrawable;
import android.os.Build;
import android.os.Bundle;
import android.util.Log;
import android.view.Gravity;
import android.view.View;
import android.view.WindowInsets;
import android.widget.Button;
import android.widget.FrameLayout;
import android.widget.LinearLayout;
import android.widget.ImageView;
import android.widget.ScrollView;
import android.widget.TextView;

import org.json.JSONException;

import java.io.File;
import java.io.IOException;
import java.io.InputStream;
import java.util.ArrayList;
import java.util.List;
import java.util.LinkedHashMap;
import java.util.Map;

public final class MainActivity extends Activity {
    private int paper, ink, primary, palePurple, paleGreen, starInk;

    private void loadDesignColors() {
        paper = getColor(R.color.surface);
        ink = getColor(R.color.text_primary);
        primary = getColor(R.color.primary);
        palePurple = getColor(R.color.primary_light);
        paleGreen = getColor(R.color.instruction_surface);
        starInk = getColor(R.color.star_ink);
    }

    private enum Screen { CHOOSER, HOME, CATALOGUE, INSTRUCTIONS, ROUND, COMPLETE }

    private List<GameDefinition> games;
    private String previewMessage;
    private Screen screen = Screen.CATALOGUE;
    private String year;
    private String subject;
    private String topicSubject;
    private String topic;
    private GameDefinition game;
    private GameRound round;
    private MatchingRound matchingRound;
    private ScrollView scroll;
    private final List<Child> children = new ArrayList<>();
    private Child selectedChild;
    private boolean profilesDamaged;
    private static final String PROFILES = "children";

    private static final class Child {
        final String id;
        final String name;
        Child(String id, String name) { this.id = id; this.name = name; }
    }

    @Override
    protected void onCreate(Bundle savedState) {
        super.onCreate(savedState);
        loadDesignColors();
        configureSystemBars();
        try {
            games = GameDefinition.loadCatalogue(getAssets());
        } catch (IOException | JSONException error) {
            Log.e("AppForKids", "Could not open the bundled catalogue", error);
            heading(page(), "Les jeux ne sont pas disponibles.", 28);
            return;
        }

        loadWorksheetPreview();
        if (!BuildConfig.DEBUG) {
            loadChildren();
            screen = Screen.CHOOSER;
        }
        if (savedState != null) {
            if (BuildConfig.DEBUG) {
                restoreScreen(savedState);
            } else if (getLastNonConfigurationInstance() != null) {
                String childId = savedState.getString("childId");
                for (Child child : children) {
                    if (child.id.equals(childId)) selectedChild = child;
                }
                if (selectedChild != null && !profilesDamaged) restoreScreen(savedState);
            }
        }
        render();
    }

    @Override
    public Object onRetainNonConfigurationInstance() {
        // A configuration change can resume the round, but a fresh process starts at the chooser.
        return Boolean.TRUE;
    }

    private void restoreScreen(Bundle state) {
        screen = Screen.valueOf(state.getString("screen", Screen.CATALOGUE.name()));
        year = state.getString("year");
        subject = state.getString("subject");
        topicSubject = state.getString("topicSubject");
        topic = state.getString("topic");
        if (screen == Screen.HOME || screen == Screen.CATALOGUE) {
            return;
        }

        String gameId = state.getString("game");
        for (GameDefinition entry : games) {
            if (entry.id.equals(gameId)) {
                game = entry;
                break;
            }
        }
        if (game == null) {
            screen = Screen.CATALOGUE;
            return;
        }
        if (screen == Screen.INSTRUCTIONS) {
            return;
        }

        // Older saved rounds predate revision metadata. Only resume their starter revision.
        String oldType = state.containsKey("matches") ? GameDefinition.Type.MATCHING.name()
                : GameDefinition.Type.TAP_TO_CHOOSE.name();
        if (game.revision != state.getInt("gameRevision", 1)
                || !game.type.name().equals(state.getString("gameType", oldType))) {
            screen = Screen.INSTRUCTIONS;
            return;
        }
        if (game.type == GameDefinition.Type.MATCHING) {
            matchingRound = MatchingRound.restore(game.pairs, state.getIntegerArrayList("matches"),
                    state.getInt("selectedPair", MatchingRound.NO_SELECTION),
                    state.getString("matchingFeedback"));
            if (matchingRound == null || (screen == Screen.COMPLETE && !matchingRound.isComplete())) {
                screen = Screen.INSTRUCTIONS;
            }
        } else {
            int question = state.getInt("question");
            if (question < 0 || question >= game.questions.size()) {
                screen = Screen.INSTRUCTIONS;
                return;
            }
            String feedback = state.getString("feedback", GameRound.Feedback.NONE.name());
            round = new GameRound(game, question, GameRound.Feedback.valueOf(feedback));
        }
    }

    @Override
    protected void onSaveInstanceState(Bundle state) {
        super.onSaveInstanceState(state);
        state.putString("screen", screen.name());
        if (selectedChild != null) state.putString("childId", selectedChild.id);
        state.putString("year", year);
        state.putString("subject", subject);
        state.putString("topicSubject", topicSubject);
        state.putString("topic", topic);
        if (game != null) {
            state.putString("game", game.id);
            state.putInt("gameRevision", game.revision);
            state.putString("gameType", game.type.name());
        }
        if (round != null) {
            state.putInt("question", round.questionIndex());
            state.putString("feedback", round.feedback().name());
        }
        if (matchingRound != null) {
            state.putIntegerArrayList("matches", matchingRound.matchedPairs());
            state.putInt("selectedPair", matchingRound.selected());
            state.putString("matchingFeedback", matchingRound.feedbackMessage());
        }
    }

    @Override
    @SuppressWarnings("deprecation")
    public void onBackPressed() {
        if (screen == Screen.CHOOSER || (BuildConfig.DEBUG && screen == Screen.CATALOGUE)) {
            super.onBackPressed();
        } else if (screen == Screen.HOME || screen == Screen.CATALOGUE) {
            changeChild();
        } else {
            show(Screen.CATALOGUE);
        }
    }

    private void loadWorksheetPreview() {
        if (!BuildConfig.DEBUG) {
            return;
        }

        previewMessage = "Aperçu du brouillon";
        File draft = getFileStreamPath("worksheet-draft.json");
        if (!draft.exists()) {
            return;
        }

        try (InputStream input = openFileInput(draft.getName())) {
            GameDefinition candidate = GameDefinition.load(input, getAssets());
            for (int index = 0; index < games.size(); index++) {
                if (games.get(index).id.equals(candidate.id)) {
                    games.set(index, candidate);
                    return;
                }
            }
            games.add(candidate);
        } catch (IOException | JSONException error) {
            previewMessage = "Impossible d’ouvrir le brouillon.";
        }
    }

    private void configureSystemBars() {
        if (Build.VERSION.SDK_INT >= 30) {
            getWindow().setDecorFitsSystemWindows(false);
            getWindow().setStatusBarColor(Color.TRANSPARENT);
            getWindow().setNavigationBarColor(Color.TRANSPARENT);
        } else {
            getWindow().setStatusBarColor(paper);
            getWindow().setNavigationBarColor(Build.VERSION.SDK_INT >= 27 ? paper : ink);
        }
    }

    private void show(Screen next) {
        screen = next;
        render();
    }

    private void render() {
        render(false);
    }

    private void render(boolean announceFeedback) {
        LinearLayout content = page();
        if (!BuildConfig.DEBUG && selectedChild != null && screen != Screen.CHOOSER) {
            body(content, "Pour " + selectedChild.name);
            button(content, "Changer d’enfant", 20, false, this::changeChild);
        }
        switch (screen) {
            case CHOOSER:
                heading(content, "Qui va jouer ?", 42);
                body(content, "Les profils restent sur cet appareil. Effacer les données ou désinstaller l’application les supprime. Les sauvegardes et transferts dépendent de l’appareil.");
                if (profilesDamaged) {
                    body(content, "Impossible de lire les profils. Ferme et rouvre l’application. Les données n’ont pas été remplacées.");
                    button(content, "Effacer les profils endommagés", 20, false, () -> parentCheck(() ->
                            new AlertDialog.Builder(this).setTitle("Effacer tous les profils ?")
                            .setMessage("Tous les profils et leur progression locale seront perdus.")
                            .setNegativeButton("Annuler", null).setPositiveButton("Effacer", (d, w) -> {
                                if (saveChildren(new ArrayList<>())) { profilesDamaged = false; render(); }
                            }).show()));
                    break;
                }
                if (children.isEmpty()) body(content, "Demande à un parent d’ajouter un enfant.");
                for (Child child : children) {
                    button(content, child.name, 30, true, () -> { selectedChild = child; show(Screen.CATALOGUE); });
                    button(content, "Supprimer " + child.name, 18, false,
                            () -> parentCheck(() -> confirmDeletion(child)));
                }
                button(content, "Ajouter un enfant", 24, false, () -> parentCheck(this::addChild));
                break;
            case HOME:
            case CATALOGUE:
                heading(content, "Les jeux", 38);
                renderFilters(content);
                int count = 0;
                for (GameDefinition entry : games) {
                    if (matchesFilters(entry)) {
                        count++;
                        LinearLayout card = card(content, Color.WHITE);
                        body(card, entry.year);
                        body(card, entry.objective);
                        body(card, entry.classificationLabel);
                        button(card, entry.title, 26, true, () -> {
                            game = entry;
                            round = null;
                            matchingRound = null;
                            show(Screen.INSTRUCTIONS);
                        });
                    }
                }
                if (count == 0) body(content, "Aucun jeu pour ce choix.");
                break;
            case INSTRUCTIONS:
                heading(content, game.title, 38);
                LinearLayout example = card(content, paleGreen);
                body(example, game.instructions);
                heading(example, game.workedExample, 28);
                button(content, "Jouer", 26, true, this::startRound);
                catalogueButton(content);
                break;
            case ROUND:
                if (game.type == GameDefinition.Type.MATCHING) {
                    new MatchingBoard(content);
                } else {
                    renderRound(content, announceFeedback);
                }
                break;
            case COMPLETE:
                heading(content, "Partie terminée !", 42);
                body(content, game.completionMessage);
                button(content, "Rejouer", 26, true, this::startRound);
                catalogueButton(content);
                break;
        }
    }

    private void changeChild() {
        selectedChild = null;
        game = null;
        round = null;
        matchingRound = null;
        show(Screen.CHOOSER);
    }

    private void loadChildren() {
        try {
            String data = getPreferences(MODE_PRIVATE).getString(PROFILES, "[]");
            JSONArray list = new JSONArray(data);
            for (int i = 0; i < list.length(); i++) {
                JSONObject item = list.getJSONObject(i);
                String id = item.getString("id");
                String name = item.getString("name");
                if (id.isEmpty() || name.isEmpty()) throw new JSONException("Invalid profile");
                for (Child existing : children) {
                    if (existing.id.equals(id) || existing.name.equalsIgnoreCase(name))
                        throw new JSONException("Duplicate profile");
                }
                children.add(new Child(id, name));
            }
        } catch (JSONException | ClassCastException error) {
            children.clear();
            profilesDamaged = true;
        }
    }

    private boolean saveChildren(List<Child> updated) {
        JSONArray list = new JSONArray();
        try {
            for (Child child : updated) {
                JSONObject item = new JSONObject();
                item.put("id", child.id);
                item.put("name", child.name);
                list.put(item);
            }
        } catch (JSONException error) { return false; }
        if (!getPreferences(MODE_PRIVATE).edit().putString(PROFILES, list.toString()).commit()) return false;
        children.clear();
        children.addAll(updated);
        return true;
    }

    private void parentCheck(Runnable passed) {
        EditText answer = new EditText(this);
        answer.setInputType(InputType.TYPE_CLASS_NUMBER);
        AlertDialog dialog = new AlertDialog.Builder(this).setTitle("Vérification pour les parents")
                .setMessage("Combien font 7 + 5 ?").setView(answer)
                .setNegativeButton("Annuler", null).setPositiveButton("Vérifier", null).create();
        dialog.setOnShowListener(ignored -> dialog.getButton(AlertDialog.BUTTON_POSITIVE).setOnClickListener(v -> {
            if (!answer.getText().toString().equals("12")) {
                answer.setError("Essaie encore.");
                return;
            }
            dialog.dismiss();
            passed.run();
        }));
        dialog.show();
    }

    private boolean containsControl(String value) {
        for (int i = 0; i < value.length(); i++) {
            if (Character.isISOControl(value.charAt(i))) return true;
        }
        return false;
    }

    private void addChild() {
        EditText name = new EditText(this);
        name.setSingleLine(true);
        name.setHint("Prénom ou surnom");
        AlertDialog dialog = new AlertDialog.Builder(this).setTitle("Ajouter un enfant")
                .setMessage("Un prénom ou surnom suffit.").setView(name)
                .setNegativeButton("Annuler", null).setPositiveButton("Ajouter", null).create();
        dialog.setOnShowListener(ignored -> dialog.getButton(AlertDialog.BUTTON_POSITIVE).setOnClickListener(v -> {
            String value = name.getText().toString().trim();
            if (value.isEmpty() || value.length() > 40 || containsControl(value)) {
                name.setError("Saisis un nom de 1 à 40 caractères, sans caractères de contrôle.");
                return;
            }
            for (Child child : children) {
                if (child.name.toLowerCase(Locale.ROOT).equals(value.toLowerCase(Locale.ROOT))) {
                    name.setError("Ce nom existe déjà. Choisis un autre surnom.");
                    return;
                }
            }
            List<Child> updated = new ArrayList<>(children);
            updated.add(new Child(UUID.randomUUID().toString(), value));
            if (!saveChildren(updated)) { name.setError("Enregistrement impossible. Réessaie."); return; }
            dialog.dismiss();
            render();
        }));
        dialog.show();
    }

    private void confirmDeletion(Child child) {
        new AlertDialog.Builder(this).setTitle("Supprimer " + child.name + " ?")
                .setMessage("Son profil et sa progression locale seront supprimés de cet appareil. Les autres enfants et les jeux restent disponibles.")
                .setNegativeButton("Annuler", null).setPositiveButton("Supprimer", (dialog, which) -> {
                    List<Child> updated = new ArrayList<>(children);
                    updated.remove(child);
                    if (!saveChildren(updated)) {
                        new AlertDialog.Builder(this).setMessage("Suppression impossible. Réessaie.").setPositiveButton("OK", null).show();
                        return;
                    }
                    render();
                }).show();
    }

    private boolean matchesFilters(GameDefinition entry) {
        if (year != null && !year.equals(entry.year)) return false;
        boolean subjectMatch = subject == null;
        boolean topicMatch = topic == null;
        for (GameDefinition.Classification classification : entry.classifications) {
            if (classification.subject.equals(subject)) subjectMatch = true;
            if (classification.subject.equals(topicSubject) && classification.topics.contains(topic)) {
                topicMatch = true;
            }
        }
        return subjectMatch && topicMatch;
    }

    private void renderFilters(LinearLayout content) {
        Map<String, String> subjects = new LinkedHashMap<>();
        Map<String, String> topics = new LinkedHashMap<>();
        for (GameDefinition entry : games) {
            for (GameDefinition.Classification item : entry.classifications) {
                subjects.put(item.subject, item.subjectLabel);
                for (int i = 0; i < item.topics.size(); i++) {
                    topics.put(item.subject + "\n" + item.topics.get(i), item.topicLabels.get(i));
                }
            }
        }
        button(content, "Année : " + (year == null ? "Toutes" : year), 20, false, () -> {
            String[] options = {"Toutes les années", "P1", "P3"};
            new AlertDialog.Builder(this).setTitle("Année").setItems(options, (dialog, index) -> {
                year = index == 0 ? null : options[index];
                render();
            }).show();
        });
        button(content, "Matière : " + (subject == null ? "Toutes" : subjects.get(subject)), 20, false, () -> {
            List<String> keys = new ArrayList<>(subjects.keySet());
            List<String> labels = new ArrayList<>();
            labels.add("Toutes les matières");
            labels.addAll(subjects.values());
            new AlertDialog.Builder(this).setTitle("Matière").setItems(labels.toArray(new String[0]), (dialog, index) -> {
                subject = index == 0 ? null : keys.get(index - 1);
                render();
            }).show();
        });
        String topicKey = topicSubject + "\n" + topic;
        button(content, "Sujet : " + (topic == null ? "Tous" : topics.get(topicKey)), 20, false, () -> {
            List<String> keys = new ArrayList<>(topics.keySet());
            List<String> labels = new ArrayList<>();
            labels.add("Tous les sujets");
            labels.addAll(topics.values());
            new AlertDialog.Builder(this).setTitle("Sujet").setItems(labels.toArray(new String[0]), (dialog, index) -> {
                if (index == 0) {
                    topicSubject = null;
                    topic = null;
                } else {
                    String[] parts = keys.get(index - 1).split("\n", 2);
                    topicSubject = parts[0];
                    topic = parts[1];
                }
                render();
            }).show();
        });
        button(content, "Effacer les filtres", 20, false, () -> {
            year = null;
            subject = null;
            topicSubject = null;
            topic = null;
            render();
        });
    }

    private void startRound() {
        if (game.type == GameDefinition.Type.MATCHING) {
            matchingRound = new MatchingRound(game.pairs);
        } else {
            round = new GameRound(game);
        }
        show(Screen.ROUND);
    }

    private void renderRound(LinearLayout content, boolean announceFeedback) {
        GameDefinition.Question question = round.question();
        body(content, getString(R.string.question_progress,
                round.questionIndex() + 1, round.questionCount()));
        heading(content, question.prompt, 34);
        LinearLayout visual = card(content, paleGreen);
        for (String row : question.visualRows) {
            TextView symbols = text(row, 38, starInk);
            symbols.setGravity(Gravity.CENTER);
            visual.addView(symbols);
        }

        if (!round.isAnswered()) {
            LinearLayout choices = new LinearLayout(this);
            choices.setOrientation(LinearLayout.HORIZONTAL);
            add(content, choices, 14);
            for (String choice : question.choices) {
                Button button = makeButton(choice, 32, false, () -> {
                    round.answer(choice);
                    render(true);
                });
                LinearLayout.LayoutParams params = new LinearLayout.LayoutParams(0, -2, 1);
                if (choices.getChildCount() > 0) {
                    params.setMarginStart(dp(10));
                }
                choices.addView(button, params);
            }
        }

        renderFeedback(content, round.feedbackMessage(), announceFeedback);
        if (round.isAnswered()) {
            button(content, round.isLastQuestion() ? "Terminer" : "Suivant", 26, true,
                    () -> show(round.advanceToNextQuestion() ? Screen.ROUND : Screen.COMPLETE));
        }
        catalogueButton(content);
    }

    private final class MatchingBoard {
        private final TextView progress;
        private final TextView selection;
        private final LinearLayout feedbackCard;
        private final TextView feedback;
        private final Button finish;
        private final Button[] leftTiles = new Button[game.pairs.size()];
        private final Button[] rightTiles = new Button[game.pairs.size()];

        MatchingBoard(LinearLayout content) {
            heading(content, game.title, 34);
            progress = body(content, "");
            selection = body(content, "");

            LinearLayout board = new LinearLayout(MainActivity.this);
            board.setOrientation(LinearLayout.HORIZONTAL);
            // The French instructions refer to the physical left and right columns.
            board.setLayoutDirection(View.LAYOUT_DIRECTION_LTR);
            add(content, board, 6);
            LinearLayout left = column(board, "À gauche", 8);
            LinearLayout right = column(board, "À droite", 0);
            for (int i = 0; i < leftTiles.length; i++) {
                int leftIndex = i;
                leftTiles[leftIndex] = makeButton(game.pairs.get(leftIndex).left, 26, false,
                        () -> select(leftIndex));
                add(left, leftTiles[leftIndex], 8);

                // Offset the answers so the halves of a pair start on different rows.
                int rightIndex = (i + 1) % rightTiles.length;
                rightTiles[rightIndex] = makeButton(game.pairs.get(rightIndex).right, 26, false,
                        () -> match(rightIndex));
                add(right, rightTiles[rightIndex], 8);
            }
            feedbackCard = card(content, palePurple);
            feedback = body(feedbackCard, "");
            finish = makeButton("Terminer", 26, true, () -> show(Screen.COMPLETE));
            add(content, finish, 12);
            catalogueButton(content);
            refresh();
        }

        private LinearLayout column(LinearLayout board, String label, int endMargin) {
            LinearLayout column = new LinearLayout(MainActivity.this);
            column.setOrientation(LinearLayout.VERTICAL);
            LinearLayout.LayoutParams params = new LinearLayout.LayoutParams(0, -2, 1);
            params.setMarginEnd(dp(endMargin));
            board.addView(column, params);
            heading(column, label, 20);
            return column;
        }

        private void select(int index) {
            matchingRound.select(index);
            refresh();
            selection.announceForAccessibility(selection.getText());
        }

        private void match(int index) {
            boolean hadKeyboardFocus = rightTiles[index].hasFocus();
            matchingRound.match(index);
            refresh();
            if (hadKeyboardFocus && matchingRound.isMatched(index)) {
                moveKeyboardFocus();
            }
            feedback.announceForAccessibility(feedback.getText());
        }

        private void moveKeyboardFocus() {
            if (matchingRound.isComplete()) {
                finish.requestFocus();
                return;
            }
            for (Button tile : leftTiles) {
                if (tile.isEnabled() && tile.requestFocus()) {
                    return;
                }
            }
        }

        private void refresh() {
            int selected = matchingRound.selected();
            boolean complete = matchingRound.isComplete();
            progress.setText(getString(R.string.pair_progress, matchingRound.matchedCount(),
                    leftTiles.length));
            selection.setText(selected == MatchingRound.NO_SELECTION
                    ? "Touche un mot à gauche."
                    : getString(R.string.chosen_word, game.pairs.get(selected).left));
            selection.setVisibility(complete ? View.GONE : View.VISIBLE);
            for (int i = 0; i < leftTiles.length; i++) {
                boolean matched = matchingRound.isMatched(i);
                refreshTile(leftTiles[i], game.pairs.get(i).left, matched, i == selected, true);
                refreshTile(rightTiles[i], game.pairs.get(i).right, matched, false,
                        selected != MatchingRound.NO_SELECTION);
            }
            String message = matchingRound.feedbackMessage();
            feedback.setText(message);
            feedbackCard.setVisibility(message == null ? View.GONE : View.VISIBLE);
            finish.setVisibility(complete ? View.VISIBLE : View.GONE);
        }

        private void refreshTile(Button tile, String label, boolean matched,
                                 boolean selected, boolean available) {
            tile.setEnabled(available && !matched);
            tile.setFocusable(available && !matched);
            if (tile.isSelected() != selected) {
                tile.setSelected(selected);
                styleButton(tile, selected);
            }
            if (matched && tile.getContentDescription() == null) {
                tile.setText("✓ " + label);
                tile.setContentDescription(getString(R.string.matched_word, label));
            }
        }
    }

    private void renderFeedback(LinearLayout content, String message, boolean announceFeedback) {
        if (message != null) {
            body(card(content, palePurple), message);
            if (announceFeedback) {
                scroll.announceForAccessibility(message);
            }
        }
    }

    private void catalogueButton(LinearLayout content) {
        button(content, "Retour au catalogue", 20, false, () -> show(Screen.CATALOGUE));
    }

    private LinearLayout page() {
        scroll = new ScrollView(this);
        scroll.setBackgroundColor(paper);
        scroll.setFillViewport(true);
        if (Build.VERSION.SDK_INT >= 30) {
            scroll.setOnApplyWindowInsetsListener((view, insets) -> {
                Insets safeArea = insets.getInsets(
                        WindowInsets.Type.systemBars() | WindowInsets.Type.displayCutout());
                view.setPadding(safeArea.left, safeArea.top, safeArea.right, safeArea.bottom);
                return insets;
            });
        }

        FrameLayout frame = new FrameLayout(this);
        scroll.addView(frame, new ScrollView.LayoutParams(-1, -2));
        LinearLayout content = new LinearLayout(this);
        content.setOrientation(LinearLayout.VERTICAL);
        content.setPadding(dp(20), dp(24), dp(20), dp(24));
        int width = Math.min(getResources().getConfiguration().screenWidthDp, 720);
        frame.addView(content, new FrameLayout.LayoutParams(dp(width), -2, Gravity.CENTER_HORIZONTAL));
        setContentView(scroll);
        ImageView landscape = new ImageView(this);
        landscape.setImageResource(R.drawable.petits_pas_landscape);
        landscape.setScaleType(ImageView.ScaleType.FIT_CENTER);
        landscape.setImportantForAccessibility(View.IMPORTANT_FOR_ACCESSIBILITY_NO);
        content.addView(landscape, new LinearLayout.LayoutParams(-1, dp(56)));
        TextView identity = text(getString(R.string.app_name), 20, primary);
        identity.setTypeface(Typeface.DEFAULT, Typeface.BOLD);
        add(content, identity, 4);
        if (BuildConfig.DEBUG) {
            body(content, previewMessage);
        }
        return content;
    }

    private LinearLayout card(LinearLayout parent, int color) {
        LinearLayout card = new LinearLayout(this);
        card.setOrientation(LinearLayout.VERTICAL);
        card.setBackground(rounded(color, 24));
        card.setPadding(dp(18), dp(12), dp(18), dp(14));
        add(parent, card, 14);
        return card;
    }

    private void heading(LinearLayout parent, String label, int size) {
        TextView heading = text(label, size, ink);
        heading.setTypeface(Typeface.DEFAULT, Typeface.BOLD);
        if (Build.VERSION.SDK_INT >= 28) {
            heading.setAccessibilityHeading(true);
        }
        add(parent, heading, 6);
    }

    private TextView body(LinearLayout parent, String label) {
        TextView body = text(label, 22, ink);
        add(parent, body, 4);
        return body;
    }

    private TextView text(String label, int size, int color) {
        TextView view = new TextView(this);
        view.setText(label);
        view.setTextSize(size);
        view.setTextColor(color);
        return view;
    }

    private void button(LinearLayout parent, String label, int size, boolean main, Runnable action) {
        add(parent, makeButton(label, size, main, action), 12);
    }

    private Button makeButton(String label, int size, boolean main, Runnable action) {
        Button button = new Button(this);
        button.setText(label);
        button.setTextSize(size);
        button.setAllCaps(false);
        button.setMinHeight(dp(64));
        button.setPadding(dp(10), dp(8), dp(10), dp(8));
        styleButton(button, main);
        button.setOnClickListener(view -> action.run());
        return button;
    }

    private void styleButton(Button button, boolean main) {
        button.setTextColor(new ColorStateList(
                new int[][]{new int[]{-android.R.attr.state_enabled}, new int[]{}},
                new int[]{ink, main ? Color.WHITE : primary}));
        int ripple = main ? 0x55ffffff : 0x335630a5;
        StateListDrawable states = new StateListDrawable();
        GradientDrawable disabled = rounded(0xffe2e5eb, 18);
        disabled.setStroke(dp(2), 0xff737c8f);
        states.addState(new int[]{-android.R.attr.state_enabled}, disabled);
        GradientDrawable focused = rounded(main ? primary : palePurple, 18);
        focused.setStroke(dp(3), main ? Color.WHITE : primary);
        states.addState(new int[]{android.R.attr.state_focused}, focused);
        states.addState(new int[]{}, rounded(main ? primary : palePurple, 18));
        button.setBackground(new RippleDrawable(ColorStateList.valueOf(ripple), states, null));
    }

    private GradientDrawable rounded(int color, int radius) {
        GradientDrawable shape = new GradientDrawable();
        shape.setColor(color);
        shape.setCornerRadius(dp(radius));
        return shape;
    }

    private void add(LinearLayout parent, View child, int topMargin) {
        LinearLayout.LayoutParams params = new LinearLayout.LayoutParams(-1, -2);
        params.topMargin = dp(topMargin);
        parent.addView(child, params);
    }

    private int dp(int value) {
        return Math.round(value * getResources().getDisplayMetrics().density);
    }
}
