---
title: Privacy Policy for Calcalou Calorie Tracker
permalink: /privacy/
---

# Privacy Policy for Calcalou Calorie Tracker

**Last updated:** October 7, 2026

**Applies to:** Calcalou Calorie Tracker for iOS and Android, version 1.1 and later

## 1. Who we are

Calcalou Calorie Tracker ("Calcalou", "the app", "we", "us") is developed and operated by
Vladimir Khrolovich, an independent developer.

For anything about this policy or your data, write to **support@calcalou.com**. Privacy
requests are answered from the same address.

If you are in the European Economic Area or the United Kingdom, we act as the **data
controller** for the processing described here.

## 2. What this policy covers

This policy describes what the app actually does in versions 1.1 to 1.3: what data it
collects, who it is sent to, why, how long it is kept, and what you can do about it. Where
version 1.2 or 1.3 differs, we say so. Where a feature is optional, we say so.

Calcalou is a calorie-tracking tool, not a medical device. It does not diagnose, treat, or
prevent any condition, and its calorie figures — especially AI photo estimates — are
approximations.

## 3. Data we collect

### 3.1 Account data

When you create an account we process:

- **Email address** — required to sign in. If you use Sign in with Apple and choose "Hide
  My Email", we only ever see Apple's private relay address.
- **Display name** — optional; used to personalise the app.
- **Account identifier (user ID)** — assigned by Firebase Authentication.
- **Sign-in method** — email/password, Apple, or Google.

From version 1.2 an account is required to use the app. In version 1.1 you can use the app
without an account, but then nothing is synced and you lose your data if you remove the app.
When you first sign in to 1.2 on a device that already holds a 1.1 log, that log is added
to your account.

### 3.2 What you log in the app

Your food and activity log: each entry's calories, an optional free-text note (for
example a food name you typed or that the AI scan recognised), whether it is food eaten
or calories burned (including the automatic daily base-burn entry, if you turn base burn
on), and its date and time; your daily calorie goal and base-burn settings with their
history; and gamification data (XP and level, longest streak, achievements, challenge
progress).

This data is stored **on your device**. When you are signed in, it is also stored in your
private area of our cloud database (Google Cloud Firestore, `users/{your user ID}`).
Security rules restrict that area so that only your own signed-in account can read or
write it.

### 3.3 Food photos and AI recognition (optional, subscribers only)

If you use the AI photo scan, the photo you take or pick is sent over an encrypted
connection to our server function (Firebase Cloud Functions, region `us-central1`), which
forwards it to the **Google Gemini API** (Google LLC) for analysis. Google acts as our
processor for this request. Gemini returns a list of recognised foods with estimated
portions and calories; you decide what to save.

What happens to the image:

- It is held in memory only for the duration of the request.
- We do **not** store the photo — not in our database, not in file storage, not in logs.
  (A photo you attach to a support request is different: it is stored with that request,
  see 3.6.)
- We do not use your photos to train any model of ours.
- Google handles the image as our processor under the
  [Gemini API terms](https://ai.google.dev/gemini-api/terms) that apply to our account,
  which govern how long Google may keep it and what Google may do with it.

Alongside each scan we store two small records:

- **Usage counter** (`ai_quota`): your user ID, the date and the number of scans that day,
  used to enforce the daily limit of 50 scans. Deleted automatically after 7 days.
- **Technical log** (`ai_recognition_logs`): model name, response time, success or error
  code, and a timestamp. It contains **no user ID and no image**. It is deleted
  automatically by a retention (TTL) policy.
- **Server logs** (Google Cloud Logging): when a scan is refused or fails, the log line may
  hold your user ID, the reason (for example no active subscription, with the entitlement
  names and expiry date) and up to 200 characters of the model's text answer — never the
  photo. They are kept for 30 days and are not removed when you delete your account.

From version 1.2 the app asks for your consent before the first photo is sent.

In version 1.1, if analytics is switched on (see 3.4), the name of the first recognised food
is also sent to Firebase Analytics as an event parameter. From version 1.2 it is not: the
analytics event says only whether the scan succeeded.

### 3.4 Usage analytics (optional, off unless you allow it)

We ask for analytics consent in the app on first use, and you can change the answer at any
time in Profile → Usage analytics. When enabled, Firebase Analytics (Google) receives
events such as screen views, features used, entries added, subscription and onboarding
steps, together with an app instance identifier, device model, OS version, app version and
coarse (country-level) location derived from IP. Your account user ID is attached to these
events while analytics is enabled. When analytics is disabled, no such events are sent.
From version 1.2 the analytics SDK stays switched off from the first launch until you
answer the consent question.

### 3.5 Crash and stability reports

Crash and error reports are collected by Firebase Crashlytics (Google) in released
versions of the app so that we can fix crashes. A report contains the error and stack
trace, device model, OS and app version, and a Crashlytics installation identifier. It
does not contain your food log or your photos.

Please note: in versions 1.1 to 1.3 crash reporting is **not** governed by the analytics switch —
it is active in the released app. If you would rather it were not, write to
support@calcalou.com and we will remove the reports associated with your installation.

### 3.6 Support requests and reports about AI results (version 1.2)

You can write to us from the app (Profile → Contact support). On Android, every AI photo
result also has "Report a problem with this result"; the iOS app does not have this button
yet. When you send either, we receive your message, your
account user ID, the email address you give us (or your account's), the app version and
build, your device's operating system and version, the app language, whether you have
Premium, the last error code the app recorded, and — only if you tick the box — the photo.
A report about an AI result also carries that result: the recognised foods, the total
calories and the model's confidence.

The request — the photo included, if you attached one — is stored in our cloud database
(`support_requests`), where we read it; it is not forwarded by email. We use it only to
answer you (by email, from support@calcalou.com) and fix the problem. It is deleted when you
delete your account; you can ask us at any time to delete it sooner.

If the app cannot save the request to our database, it opens your own mail app instead,
with the message and the same technical details prefilled and no photo. That mail goes
through your own email provider, and nothing is stored in our database.

### 3.7 Notifications

Daily reminders are scheduled on your device and need the notification permission. Each
time the app starts it also registers with Firebase Cloud Messaging (Google), which issues
a **device push token** whether or not you allow notifications — the permission only
controls whether the device displays notices. The token identifies a device installation,
not you by name; it stays with Google and the app, is not sent to our own servers, and the
app currently sends no push messages.

### 3.8 Advertising

Unless you have an active Premium subscription, the app shows banner ads supplied by
**Google AdMob**. To serve, measure and report on those ads, AdMob receives your device's
advertising identifier (IDFA on iOS, Advertising ID on Android), IP address, device and
app information, and data about ad views and taps. Google is an independent controller for
this processing; see Google's own notice at
[https://business.safety.google/privacy/](https://business.safety.google/privacy/).

Your food entries, photos, weight, goals and account details are **never** shared with
advertisers.

**Consent (EEA, UK and regulated US states).** Before requesting any ad, the app shows
Google's consent form (UMP). Your choice decides whether ads are personalised. You can
reopen the form at any time from Profile → Ad Privacy Options.

**App Tracking Transparency (iOS).** iOS shows the "Allow app to track" prompt. If you
**allow**, the IDFA may be used for personalised advertising and ad attribution. If you
**decline**, no IDFA is available and ads are non-personalised — ads still appear, and
nothing else in the app changes. You can change this later in iOS Settings → Privacy &
Security → Tracking.

Subscribers see no ads and no ad requests are made for them.

### 3.9 Subscriptions and purchases

Subscriptions are sold by **Apple** (App Store) or **Google** (Play Store). They collect
the payment; we never see your card number or billing address.

We use **RevenueCat, Inc.** to check whether a subscription is active. RevenueCat receives
your account user ID, the product purchased, the purchase and renewal or expiry dates, the
store receipt and basic device and country data. Our server also asks RevenueCat whether
your account has an active subscription before it accepts an AI scan.

### 3.10 Remote configuration

The app fetches feature settings from Firebase Remote Config. This request carries app
instance and device information handled by Google as described in the Firebase
documentation.

### 3.11 Apple Health and Health Connect (version 1.3 and later)

Versions 1.1 and 1.2 do not use Apple Health or Health Connect. From version 1.3 the app can
connect to Apple Health on iOS and to Health Connect on Android. It is off until you turn it
on in **Profile**, and the app works the same without it. With your permission it:

- **writes** one entry per day to Apple Health ("Dietary Energy") or Health Connect
  ("Nutrition"): the total calories you logged in Calcalou that day, so other health apps can
  see it;
- **reads** the active calories burned today ("Active Energy" / "Active calories burned"),
  only to show that figure on the Today screen. It is not added to your calorie budget;
- **reads** your most recent weight from the last 30 days ("Weight" / "Body Mass"), only to
  pre-fill the weight field of the base-burn calculator. You confirm or change it, and only
  the calculated result you save is kept.

Data read from Apple Health or Health Connect stays on your device. It is not sent to our
servers or to any third party, is not included in analytics, crash reports, AI requests or
advertising, is not sold, and is not used for advertising or to build a profile of you.
Calcalou's use of information received from Health Connect adheres to the
[Health Connect Permissions policy](https://support.google.com/googleplay/android-developer/answer/9888170),
including the Limited Use requirements.

You can withdraw access at any time: turn the switch off in Profile, or remove Calcalou's
access in the Health Connect app (App permissions → Calcalou) or in iOS Settings → Health →
Data Access & Devices → Calcalou. Entries Calcalou has already written stay in Apple Health or
Health Connect until you delete them there; deleting your Calcalou account does not remove
them.

### 3.12 Children

Calcalou is not directed at children. We do not knowingly collect personal data from
children under 13 (or under the applicable minimum age in your country). If you believe a
child has given us data, write to support@calcalou.com and we will delete it.

## 4. Why we process this data, and on what legal basis

For users in the EEA and the UK, the GDPR requires us to name a legal basis for each
purpose:

| Purpose | Data | Legal basis (GDPR Art. 6) |
|---|---|---|
| Create and run your account, sync your log across devices | Account data, your log | Performance of a contract (Art. 6(1)(b)) |
| Recognise food in a photo you submit | Photo, locale | Performance of a contract (Art. 6(1)(b)) for the subscription feature; the photo is only ever sent at your request |
| Enforce the daily scan limit, prevent abuse, keep the service secure | Usage counter, technical log | Legitimate interests (Art. 6(1)(f)) — running the service sustainably |
| Manage your subscription and restore purchases | Purchase data | Performance of a contract (Art. 6(1)(b)) |
| Usage analytics | Analytics events | Consent (Art. 6(1)(a)) — the in-app switch |
| Personalised advertising | Advertising identifier, ad interactions | Consent (Art. 6(1)(a)) — the UMP form and, on iOS, ATT |
| Non-personalised advertising | Limited device and ad data | Legitimate interests (Art. 6(1)(f)) — funding a free app |
| Crash and stability reports | Diagnostic data | Legitimate interests (Art. 6(1)(f)) — keeping the app working |
| Answering a support request or a report about an AI result | The request described in 3.6 | Performance of a contract (Art. 6(1)(b)); the optional photo only because you attached it |
| Keeping push delivery possible | Device push token | Legitimate interests (Art. 6(1)(f)); showing notices and reminders needs the OS notification permission |

We do not sell your personal data, and we do not "share" it for cross-context behavioural
advertising in the sense of US state privacy laws other than through the AdMob processing
described in 3.8, which you control through the consent form and, on iOS, ATT.

## 5. Who your data is sent to

| Recipient | What they receive | Role | Where |
|---|---|---|---|
| Google (Firebase Authentication, Firestore, Cloud Functions, Remote Config, Cloud Messaging) | Account data, your synced log, AI scan requests | Processor | United States (`us-central1`) |
| Google (Gemini API) | Food photos submitted for recognition | Processor | United States |
| Google (Firebase Analytics, Crashlytics) | Analytics events, crash reports | Processor | United States |
| Google (AdMob) | Advertising identifier, ad interaction data | Independent controller | United States |
| RevenueCat, Inc. | Subscription status and receipts | Processor | United States |
| Cloudflare, Inc. (Email Routing) | Anything you email to support@calcalou.com, passed on to our inbox | Processor | United States |
| Google (Gmail) | Our email replies to you, and anything you email us | Processor | United States |
| Apple / Google Play | Your payment; we receive only the subscription status | Independent controllers | Per their own policies |

Beyond this, we disclose data only where the law requires it.

## 6. International transfers

The services above process data in the United States. Where data is transferred out of the
EEA or the UK, the transfer relies on the European Commission's Standard Contractual
Clauses (and the UK Addendum) as incorporated in our agreements with those providers. You
can ask us for details at support@calcalou.com.

## 7. How long we keep data

| Data | Retention |
|---|---|
| Account and synced log | Until you delete your account (see section 9) |
| Local data on your device | Until you delete it in the app or remove the app |
| Data read from Apple Health or Health Connect | Not stored: used on the device for display or to pre-fill a field, then discarded |
| Food photos sent for AI recognition | Not stored — held in memory for the duration of the recognition request only |
| AI usage counter (`ai_quota`) | 7 days, then deleted automatically |
| AI technical log (`ai_recognition_logs`) | Deleted automatically by a retention policy; contains no user identifier |
| Server logs of refused or failed scans | 30 days (Google Cloud Logging) |
| Analytics events | Per Firebase Analytics retention settings (currently up to 14 months) |
| Crash reports | Per Crashlytics retention (currently up to 90 days) |
| Support requests and AI-result reports, an attached photo included | Until you delete your account, or sooner on request |
| Subscription records | Kept by RevenueCat and the stores for as long as required for billing and tax purposes |

## 8. Security

Everything the app sends travels over TLS. Your synced data sits in Google Cloud
Firestore, encrypted at rest, behind security rules that allow access only to your own
signed-in account. The AI recognition endpoint requires a signed-in account and an active
subscription. Our API keys are held as server-side secrets and never ship in the app.

No system is perfectly secure, so we cannot guarantee absolute security — but we do not
ask for more data than the app needs.

## 9. Deleting your account and your data

**In the app:** Profile → Delete Account. This deletes your entries, settings, achievements,
gamification progress and your support requests (photos included) from our database, deletes your account from Firebase
Authentication, and clears the data held on the device. For security, you may be asked to
sign in again first. The action cannot be undone. If our deletion service cannot be
reached, the app still removes your account and the data above, but your support requests
stay in our database until you ask us to delete them.

**By email:** write to [support@calcalou.com](mailto:support@calcalou.com?subject=Delete%20my%20Calcalou%20account)
from the address on the account. We complete deletions within 30 days.

Deleting the app alone does not delete synced data — use Delete Account.

## 10. Your rights

Wherever you live, you can ask us to give you a copy of your data, correct it, or delete
it, and you can withdraw a consent you gave.

If you are in the EEA or the UK, the GDPR gives you the rights of access (Art. 15),
rectification (Art. 16), erasure (Art. 17), restriction (Art. 18), data portability
(Art. 20) and objection to processing based on legitimate interests (Art. 21), as well as
the right to withdraw consent at any time without affecting processing already carried out.

To exercise any of these, write to **support@calcalou.com**. We reply within one month. You
also have the right to complain to your national data protection authority.

If you are in California, you may request access to, deletion of, or correction of your
personal information, and you will not be treated differently for exercising those rights.
We do not sell personal information.

The fastest ways to act yourself:

- **Analytics:** Profile → Usage analytics
- **Ad consent:** Profile → Ad Privacy Options
- **iOS tracking:** Settings → Privacy & Security → Tracking
- **Notifications:** your device's notification settings
- **Everything:** Profile → Delete Account

## 11. Changes to this policy

We will update this page when the app changes, and the "Last updated" date at the top will
change with it. Material changes will also be announced in the app or by email.

## 12. Contact

**Email:** [support@calcalou.com](mailto:support@calcalou.com)

**Support:** [Calcalou Support](/support/)
