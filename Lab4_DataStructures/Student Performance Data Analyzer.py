"""Generate and summarize individualized student performance records."""

from collections import Counter, defaultdict
import random


# Student-specific inputs
LAST_NAME = "COPON"
STUDENT_ID = "TUPM-26-1942"
SEED_NUM = 2
FAVORITE_ARTIST = "LEVERFALL"

SUBJECTS = [
    "PROGRAMMING",
    "MATHEMATICS",
    "ELECTRONICS",
    "PHYSICS",
    "ENGLISH",
]
PERFORMANCE_CATEGORIES = (
    (90, "Excellent"),
    (80, "Good"),
    (75, "Satisfactory"),
    (0, "Needs Improvement"),
)


def artist_position_score(artist: str) -> int:
    """Weight each letter's A1Z26 value by its 1-based position in the name."""
    return sum(
        position * (ord(character.upper()) - ord("A") + 1)
        for position, character in enumerate(artist, start=1)
        if character.isalpha()
    )


def performance_category(score: int | None) -> str:
    if score is None:
        return "Incomplete"
    for minimum, category in PERFORMANCE_CATEGORIES:
        if score >= minimum:
            return category
    raise ValueError(f"Score out of range: {score}")


def generate_records() -> list[dict[str, int | str | None]]:
    students = [f"{LAST_NAME}-{number:02d}" for number in range(1, 6)]
    score_seed = SEED_NUM * 100_000 + artist_position_score(FAVORITE_ARTIST)
    score_generator = random.Random(score_seed)

    records: list[dict[str, int | str | None]] = []
    for student in students:
        for subject in SUBJECTS:
            records.append(
                {
                    "student": student,
                    "subject": subject,
                    "score": score_generator.randint(0, 100),
                }
            )

    # Deliberately make one student-subject score unavailable.
    records[-1]["score"] = None

    # Append one extra occurrence of an existing student-subject record.
    records.append(records[0].copy())
    return records


def summarize(records: list[dict[str, int | str | None]]) -> tuple[
    list[dict[str, int | str | None]],
    dict[str, list[int]],
    dict[str, list[int]],
    Counter[str],
    list[tuple[str, str]],
    list[tuple[str, str]],
]:
    pair_counts = Counter((record["student"], record["subject"]) for record in records)
    repeated_pairs = sorted(pair for pair, count in pair_counts.items() if count > 1)

    seen_pairs: set[tuple[str | None, str | None]] = set()
    unique_valid_records: list[dict[str, int | str | None]] = []
    student_scores: dict[str, list[int]] = defaultdict(list)
    subject_scores: dict[str, list[int]] = defaultdict(list)
    categories: Counter[str] = Counter()
    incomplete_records: list[tuple[str, str]] = []

    for record in records:
        student = record["student"]
        subject = record["subject"]
        score = record["score"]
        pair = (student, subject)

        if score is None:
            incomplete_records.append((str(student), str(subject)))
            continue
        if pair in seen_pairs:
            continue

        seen_pairs.add(pair)
        numeric_score = int(score)
        unique_valid_records.append(record)
        student_scores[str(student)].append(numeric_score)
        subject_scores[str(subject)].append(numeric_score)
        categories[performance_category(numeric_score)] += 1

    return (
        unique_valid_records,
        student_scores,
        subject_scores,
        categories,
        repeated_pairs,
        incomplete_records,
    )


def average(scores: list[int]) -> float:
    return sum(scores) / len(scores) if scores else 0.0


def main() -> None:
    records = generate_records()
    (
        unique_valid_records,
        student_scores,
        subject_scores,
        categories,
        repeated_pairs,
        incomplete_records,
    ) = summarize(records)
    occurrence_count: Counter[tuple[str | None, str | None]] = Counter()

    print("FINAL STUDENT PERFORMANCE REPORT")
    print("=" * 78)
    print(
        f"Student identity: {LAST_NAME} | ID: {STUDENT_ID} | "
        f"SEED_NUM: {SEED_NUM} | Favorite artist: {FAVORITE_ARTIST}"
    )
    print(
        "Score generation: seeded pseudo-random scores (0-100), using "
        "SEED_NUM and the artist's position-weighted A1Z26 letter values."
    )
    print(
        "Categories: Excellent 90-100; Good 80-89; Satisfactory 75-79; "
        "Needs Improvement 0-74."
    )

    print("\nGENERATED RECORDS (ordered by student, then subject)")
    print(f"{'STUDENT':<14} {'SUBJECT':<15} {'SCORE':>5}  {'CATEGORY':<20} STATUS")
    print("-" * 78)
    for record in records:
        pair = (record["student"], record["subject"])
        occurrence_count[pair] += 1
        score = record["score"]
        status = "REPEATED" if occurrence_count[pair] > 1 else "INCOMPLETE" if score is None else "OK"
        display_score = "MISSING" if score is None else str(score)
        print(
            f"{record['student']:<14} {record['subject']:<15} {display_score:>5}  "
            f"{performance_category(score):<20} {status}"
        )

    print("\nRECORD QUALITY")
    print(f"Total records: {len(records)}")
    print(f"Unique student-subject pairs: {len({(r['student'], r['subject']) for r in records})}")
    for student, subject in repeated_pairs:
        print(f"Repeated: {student} / {subject} appears {occurrence_count[(student, subject)]} times.")
    for student, subject in incomplete_records:
        print(f"Incomplete: {student} / {subject} has no score.")

    print("\nPERFORMANCE CATEGORIES (unique valid student-subject records)")
    for _, category in PERFORMANCE_CATEGORIES:
        print(f"{category:<20} {categories[category]}")
    print(f"{'Incomplete':<20} {len(incomplete_records)}")

    print("\nSTUDENT SUMMARIES (ordered by average score, highest first)")
    print(f"{'STUDENT':<14} {'VALID SCORES':>12} {'AVERAGE':>10}  CATEGORY COUNTS")
    print("-" * 78)
    student_category_counts: dict[str, Counter[str]] = defaultdict(Counter)
    for record in unique_valid_records:
        student_category_counts[str(record["student"])][
            performance_category(int(record["score"]))
        ] += 1
    for student in sorted(student_scores, key=lambda name: (-average(student_scores[name]), name)):
        counts = student_category_counts[student]
        breakdown = ", ".join(
            f"{category} {counts[category]}"
            for _, category in PERFORMANCE_CATEGORIES
            if counts[category]
        )
        print(
            f"{student:<14} {len(student_scores[student]):>12} "
            f"{average(student_scores[student]):>10.2f}  {breakdown}"
        )

    print("\nSUBJECT SUMMARIES (ordered by average score, highest first)")
    print(f"{'SUBJECT':<15} {'VALID SCORES':>12} {'AVERAGE':>10}")
    print("-" * 42)
    for subject in sorted(subject_scores, key=lambda name: (-average(subject_scores[name]), name)):
        print(
            f"{subject:<15} {len(subject_scores[subject]):>12} "
            f"{average(subject_scores[subject]):>10.2f}"
        )

    valid_scores = [int(record["score"]) for record in unique_valid_records]
    print("\nOVERALL")
    print(f"Unique valid scores: {len(valid_scores)}")
    print(f"Overall average: {average(valid_scores):.2f}")


if __name__ == "__main__":
    main()
