package be.hershalpandya.appforkids;

import android.app.Activity;
import android.content.res.ColorStateList;
import android.graphics.Color;
import android.graphics.Insets;
import android.graphics.Typeface;
import android.graphics.drawable.GradientDrawable;
import android.graphics.drawable.RippleDrawable;
import android.os.Build;
import android.os.Bundle;
import android.util.Log;
import android.view.Gravity;
import android.view.View;
import android.view.WindowInsets;
import android.widget.Button;
import android.widget.FrameLayout;
import android.widget.LinearLayout;
import android.widget.ScrollView;
import android.widget.TextView;

import org.json.JSONException;

import java.io.File;
import java.io.IOException;
import java.io.InputStream;
import java.util.ArrayList;
import java.util.List;

public final class MainActivity extends Activity {
    private static final int PAPER = 0xfff8f5ed;
    private static final int INK = 0xff20283d;
    private static final int BLUE = 0xff2257a5;
    private static final int PALE_BLUE = 0xffe9f0ff;
    private static final int PALE_YELLOW = 0xffffedb0;
    private static final int STAR = 0xff7e4503;

    private enum Screen { HOME, CATALOGUE, INSTRUCTIONS, ROUND, COMPLETE }

    private List<GameDefinition> games;
    private String previewMessage;
    private Screen screen = Screen.HOME;
    private String year;
    private GameDefinition game;
    private GameRound round;
    private MatchingRound matchingRound;
    private ScrollView scroll;

    @Override
    protected void onCreate(Bundle savedState) {
        super.onCreate(savedState);
        configureSystemBars();
        try {
            games = GameDefinition.loadCatalogue(getAssets());
        } catch (IOException | JSONException error) {
            Log.e("AppForKids", "Could not open the bundled catalogue", error);
            heading(page(), "Les jeux ne sont pas disponibles.", 28);
            return;
        }

        loadWorksheetPreview();

        if (savedState != null) {
            restoreScreen(savedState);
        }
        render();
    }

    private void restoreScreen(Bundle state) {
        screen = Screen.valueOf(state.getString("screen", Screen.HOME.name()));
        year = state.getString("year");
        if (screen == Screen.HOME || screen == Screen.CATALOGUE) {
            return;
        }

        String gameId = state.getString("game");
        for (GameDefinition entry : games) {
            if (entry.id.equals(gameId) && entry.year.equals(year)) {
                game = entry;
                break;
            }
        }
        if (game == null) {
            screen = year == null ? Screen.HOME : Screen.CATALOGUE;
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
        state.putString("year", year);
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
        if (screen == Screen.HOME) {
            super.onBackPressed();
        } else {
            show(screen == Screen.CATALOGUE ? Screen.HOME : Screen.CATALOGUE);
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
            getWindow().setStatusBarColor(PAPER);
            getWindow().setNavigationBarColor(Build.VERSION.SDK_INT >= 27 ? PAPER : INK);
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
        switch (screen) {
            case HOME:
                if (BuildConfig.DEBUG) {
                    body(content, previewMessage);
                }
                heading(content, "À toi de jouer !", 42);
                body(content, "Choisis ton année");
                yearButton(content, "P1");
                yearButton(content, "P3");
                break;
            case CATALOGUE:
                heading(content, year + " · Les jeux", 38);
                for (GameDefinition entry : games) {
                    if (entry.year.equals(year)) {
                        LinearLayout card = card(content, Color.WHITE);
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
                button(content, "Changer d’année", 20, false, () -> show(Screen.HOME));
                break;
            case INSTRUCTIONS:
                heading(content, game.title, 38);
                LinearLayout example = card(content, PALE_YELLOW);
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

    private void yearButton(LinearLayout content, String selectedYear) {
        button(content, selectedYear, 32, true, () -> {
            year = selectedYear;
            show(Screen.CATALOGUE);
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
        LinearLayout visual = card(content, PALE_YELLOW);
        for (String row : question.visualRows) {
            TextView symbols = text(row, 38, STAR);
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
            feedbackCard = card(content, PALE_BLUE);
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
            body(card(content, PALE_BLUE), message);
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
        scroll.setBackgroundColor(PAPER);
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
        TextView heading = text(label, size, INK);
        heading.setTypeface(Typeface.DEFAULT, Typeface.BOLD);
        if (Build.VERSION.SDK_INT >= 28) {
            heading.setAccessibilityHeading(true);
        }
        add(parent, heading, 6);
    }

    private TextView body(LinearLayout parent, String label) {
        TextView body = text(label, 22, INK);
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
        button.setTextColor(main ? Color.WHITE : BLUE);
        int ripple = main ? 0x55ffffff : 0x332257a5;
        button.setBackground(new RippleDrawable(
                ColorStateList.valueOf(ripple), rounded(main ? BLUE : PALE_BLUE, 18), null));
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
