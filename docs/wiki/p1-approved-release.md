# P1 approved releases

On 2026-11-27, `hershalpandya/AppForKids@77720c0` added a parent approval command that recorded an exact game ID and revision as a private snapshot. The release command took an explicit list of approved revisions, replaced games with the same ID, and published the signed APK only after validation. Recovery used the earlier approval with a higher Android version code. [Release ticket](https://github.com/hershalpandya/AppForKids/issues/4) · [Implementation PR](https://github.com/hershalpandya/AppForKids/pull/10)

On 2026-11-27, an emulator accepted the signed version-2 candidate over the historical version-1 starter APK without changing the first installation time. The revised starter and a newly approved game played offline. An invalid revision was then rejected, and the earlier approved content built again as APK version 3. [Implementation PR](https://github.com/hershalpandya/AppForKids/pull/10)

See the [P1 worksheet preview](p1-worksheet-preview.md) for the review step and the [classification contract](../classification-contract.md) for schema and legacy approval compatibility, and [Android APK testing](android-apk-testing.md) for the upgrade checks.

On 2026-11-27, the [parent handoff](parent-handoff.md) exercised validation, approval, and recovery from a failed draft using a new synthetic sample. The approved sample was installed in a family-signed update on the physical tablet.
