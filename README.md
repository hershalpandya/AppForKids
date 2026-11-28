# AppForKids

AppForKids propose deux jeux hors ligne. En **P1**, [Les étoiles à compter](app/src/main/assets/games/compter-les-etoiles.json) fait pratiquer le dénombrement. En **P3**, [Les mots de même sens](app/src/main/assets/games/les-mots-de-meme-sens.json) fait associer des synonymes. Utilise **Changer d’année** pour passer d’un catalogue à l’autre.

## Add a game or install the app

Start with the [parent guide](docs/parent-handoff.md) to set up your computer, preview and approve a game, and build and install a signed APK. It includes a practice run with a [two-page synthetic worksheet](docs/samples/parent-handoff/review.md).

## Authoring and testing reference

- [P1 counting workflow](docs/p1-worksheet-preview.md) and [P3 matching workflow](docs/p3-worksheet-preview.md) for game definitions and sample prompts.
- [Game mechanics extension guide](docs/game-mechanics.md) for the portable format and how to add an interaction.
- [GitHub Actions](docs/parent-handoff.md#find-ci-results-and-diagnostic-files) for the tested starter and update APKs and failure diagnostics.

## Development quality checks

Use Python 3.10 or newer, JDK 17, Android SDK 35, and Node.js 20.17 or newer. Install the local quality tools and Git hook in a normal checkout:

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements-dev.txt
npm ci
```

`npm ci` activates Husky by setting Git's `core.hooksPath`. In a repository with multiple worktrees that setting may be shared; coordinate it with any existing hooks. The pre-commit hook checks staged formatting, Python lint and strict types, Java formatting, shuffled Python tests with a 70% release-tool line-coverage threshold, and Android debug/release lint. It requires the SDK and `JAVA_HOME`/`ANDROID_HOME` described in the [parent guide](docs/parent-handoff.md). The Java formatter downloads a pinned, checksum-verified release on first use; set `GOOGLE_JAVA_FORMAT_JAR` to a previously downloaded copy for offline use.

To run the same checks without committing:

```bash
npm run lint:python
npm run lint:java
npm run typecheck
npm test
npm run lint:android
```

The Python coverage gate covers the production release tool; the other Python files drive tests. Android lint treats new warnings as errors; existing findings are tracked in [the lint baseline](app/lint-baseline.xml). Android line coverage needs an emulator, so CI enforces it rather than the hook: the `app-coverage` job installs the JaCoCo-instrumented `coverage` build (`be.hershalpandya.appforkids.coverage`, debug-signed, never for family devices), runs the installed-app suites in a shuffled order seeded by the run number, and fails below 70% of app lines. To replay it on a disposable, rooted, offline emulator — never a device with family data:

```bash
./gradlew :app:assembleCoverage
adb install -r app/build/outputs/apk/coverage/app-coverage.apk
APPFORKIDS_PACKAGE=be.hershalpandya.appforkids.coverage APPFORKIDS_COVERAGE_DIR=build/app-coverage python3 scripts/installed_suites.py --seed 11 build/app-coverage-reports
./gradlew :app:appCoverageReport :app:appCoverageVerification -PappforkidsCoverageData=build/app-coverage
```

See [quality practices](docs/quality-practices.md) for the reasoning behind each check.
