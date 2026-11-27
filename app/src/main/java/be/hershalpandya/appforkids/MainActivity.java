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

import java.io.IOException;
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
    private Screen screen = Screen.HOME;
    private String year;
    private GameDefinition game;
    private GameRound round;
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

        if (savedState != null) {
            screen = Screen.valueOf(savedState.getString("screen", Screen.HOME.name()));
            year = savedState.getString("year");
            String gameId = savedState.getString("game");
            for (GameDefinition entry : games) {
                if (entry.id.equals(gameId)) {
                    game = entry;
                    break;
                }
            }
            if (game != null) {
                String feedback = savedState.getString("feedback", GameRound.Feedback.NONE.name());
                round = new GameRound(game, savedState.getInt("question"),
                        GameRound.Feedback.valueOf(feedback));
            }
        }
        render();
    }

    @Override
    protected void onSaveInstanceState(Bundle state) {
        super.onSaveInstanceState(state);
        state.putString("screen", screen.name());
        state.putString("year", year);
        if (game != null) {
            state.putString("game", game.id);
        }
        if (round != null) {
            state.putInt("question", round.questionIndex());
            state.putString("feedback", round.feedback().name());
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

    private void configureSystemBars() {
        if (Build.VERSION.SDK_INT >= 30) {
            getWindow().setDecorFitsSystemWindows(false);
            getWindow().setStatusBarColor(Color.TRANSPARENT);
            getWindow().setNavigationBarColor(Color.TRANSPARENT);
        } else {
            getWindow().setStatusBarColor(PAPER);
            getWindow().setNavigationBarColor(Build.VERSION.SDK_INT >= 26 ? PAPER : INK);
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
                heading(content, "À toi de jouer !", 42);
                body(content, "Choisis ton année");
                button(content, "P1", 32, true, () -> {
                    year = "P1";
                    show(Screen.CATALOGUE);
                });
                break;
            case CATALOGUE:
                heading(content, year + " · Les jeux", 38);
                for (GameDefinition entry : games) {
                    if (entry.year.equals(year)) {
                        LinearLayout card = card(content, Color.WHITE);
                        body(card, entry.objective);
                        button(card, entry.title, 26, true, () -> {
                            game = entry;
                            round = null;
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
                renderRound(content, announceFeedback);
                break;
            case COMPLETE:
                heading(content, "Partie terminée !", 42);
                body(content, "Bravo, tu as compté tous les groupes d’étoiles.");
                button(content, "Rejouer", 26, true, this::startRound);
                catalogueButton(content);
                break;
        }
    }

    private void startRound() {
        round = new GameRound(game);
        show(Screen.ROUND);
    }

    private void renderRound(LinearLayout content, boolean announceFeedback) {
        GameDefinition.Question question = round.question();
        body(content, getString(R.string.question_progress,
                round.questionIndex() + 1, round.questionCount()));
        heading(content, question.prompt, 34);
        LinearLayout visual = card(content, PALE_YELLOW);
        for (String row : question.visualRows) {
            TextView stars = text(row, 38, STAR);
            stars.setGravity(Gravity.CENTER);
            visual.addView(stars);
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

        String message = round.feedbackMessage();
        if (message != null) {
            body(card(content, PALE_BLUE), message);
            if (announceFeedback) {
                scroll.announceForAccessibility(message);
            }
        }
        if (round.isAnswered()) {
            button(content, round.isLastQuestion() ? "Terminer" : "Suivant", 26, true,
                    () -> show(round.advanceToNextQuestion() ? Screen.ROUND : Screen.COMPLETE));
        }
        catalogueButton(content);
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

    private void body(LinearLayout parent, String label) {
        add(parent, text(label, 22, INK), 4);
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
        button.setTextColor(main ? Color.WHITE : BLUE);
        int ripple = main ? 0x55ffffff : 0x332257a5;
        button.setBackground(new RippleDrawable(
                ColorStateList.valueOf(ripple), rounded(main ? BLUE : PALE_BLUE, 18), null));
        button.setOnClickListener(view -> action.run());
        return button;
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
