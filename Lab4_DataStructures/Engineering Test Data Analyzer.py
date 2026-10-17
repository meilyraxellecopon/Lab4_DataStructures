"""Generate and summarize an individualized engineering test dataset."""

from collections import Counter, defaultdict
from dataclasses import dataclass


# Student-specific inputs
LAST_NAME = "COPON"
STUDENT_ID = "TUPM-26-1942"
SEED_NUM = 2
FAVORITE_ARTIST = "LEVERFALL"

MEASUREMENT_CATEGORIES = (
    "TEMPERATURE",
    "VOLTAGE",
    "CURRENT",
    "PRESSURE",
    "SPEED",
)

# Plausible integer ranges provide readable sample measurements for each category.
CATEGORY_RANGES = {
    "TEMPERATURE": (15, 40),
    "VOLTAGE": (100, 240),
    "CURRENT": (1, 20),
    "PRESSURE": (90, 120),
    "SPEED": (10, 180),
}


@dataclass(frozen=True)
class Measurement:
    record_id: str
    test_source: str
    category: str
    value: int


def test_sources() -> list[str]:
    return [f"T{number}-{LAST_NAME}" for number in range(1, 6)]


def measurement_value(
    source_index: int,
    category_index: int,
    measurement_index: int,
) -> int:
    artist_letters = [
        character.upper()
        for character in FAVORITE_ARTIST
        if character.isalpha()
    ]
    if not artist_letters:
        raise ValueError("FAVORITE_ARTIST must contain at least one letter.")

    artist_index = (
        SEED_NUM + source_index + category_index + measurement_index
    ) % len(artist_letters)
    artist_position = artist_index + 1
    artist_letter_value = ord(artist_letters[artist_index]) - ord("A") + 1
    minimum, maximum = CATEGORY_RANGES[MEASUREMENT_CATEGORIES[category_index]]
    value_span = maximum - minimum + 1
    generated_offset = (
        SEED_NUM
        + source_index
        + category_index
        + measurement_index
        + artist_position
        + artist_letter_value
    )
    return minimum + generated_offset % value_span


def generate_measurements() -> list[Measurement]:
    records: list[Measurement] = []
    sources = test_sources()

    for source_index, source in enumerate(sources):
        for category_index, category in enumerate(MEASUREMENT_CATEGORIES):
            records.append(
                Measurement(
                    record_id=f"R{len(records) + 1:03d}",
                    test_source=source,
                    category=category,
                    value=measurement_value(source_index, category_index, 0),
                )
            )

    # Add a second measurement for the same source/category pair.
    records.append(
        Measurement(
            record_id=f"R{len(records) + 1:03d}",
            test_source=sources[0],
            category=MEASUREMENT_CATEGORIES[0],
            value=measurement_value(0, 0, 1),
        )
    )
    return records


def grouped_values(
    records: list[Measurement],
    group_by: str,
) -> dict[str, list[int]]:
    groups: dict[str, list[int]] = defaultdict(list)
    for record in records:
        key = record.test_source if group_by == "source" else record.category
        groups[key].append(record.value)
    return groups


def summarize_values(values: list[int]) -> tuple[float, int, int]:
    return sum(values) / len(values), min(values), max(values)


def main() -> None:
    records = generate_measurements()
    source_values = grouped_values(records, "source")
    category_values = grouped_values(records, "category")
    pair_counts = Counter(
        (record.test_source, record.category) for record in records
    )
    repeated_pairs = sorted(
        (pair, count) for pair, count in pair_counts.items() if count > 1
    )

    print("FINAL ORGANIZED AND SUMMARIZED TEST DATASET")
    print("=" * 94)
    print(
        f"Student: {LAST_NAME} | ID: {STUDENT_ID} | "
        f"SEED_NUM: {SEED_NUM} | Favorite artist: {FAVORITE_ARTIST}"
    )
    print(
        "Value rule: combine SEED_NUM, source/category indexes, measurement "
        "index, and the selected artist letter's 1-based position and A1Z26 "
        "value; map the result into each category's stated range."
    )
    print("Measurement ranges: " + ", ".join(
        f"{category} {minimum}-{maximum}"
        for category, (minimum, maximum) in CATEGORY_RANGES.items()
    ))

    print("\nGENERATED TEST DATA (ordered by source, then category)")
    print(f"{'RECORD':<8} {'TEST SOURCE':<15} {'CATEGORY':<15} {'VALUE':>8}")
    print("-" * 52)
    occurrence_counts: Counter[tuple[str, str]] = Counter()
    source_order = {source: index for index, source in enumerate(test_sources())}
    category_order = {
        category: index
        for index, category in enumerate(MEASUREMENT_CATEGORIES)
    }
    for record in sorted(
        records,
        key=lambda item: (
            source_order[item.test_source],
            category_order[item.category],
            item.record_id,
        ),
    ):
        pair = (record.test_source, record.category)
        occurrence_counts[pair] += 1
        status = " REPEATED" if occurrence_counts[pair] > 1 else ""
        print(
            f"{record.record_id:<8} {record.test_source:<15} "
            f"{record.category:<15} {record.value:>8}{status}"
        )

    distinct_sources = {record.test_source for record in records}
    distinct_categories = {record.category for record in records}
    print("\nREPEATED AND DISTINCT DATA")
    for (source, category), count in repeated_pairs:
        print(f"Repeated source/category: {source} / {category} appears {count} times.")
    print(f"Distinct test sources: {len(distinct_sources)}")
    print(f"Distinct measurement categories: {len(distinct_categories)}")
    print(f"Distinct source/category pairs: {len(pair_counts)}")
    print(f"Repeated source/category pairs: {len(repeated_pairs)}")
    print(
        "Measurements per category: "
        + ", ".join(
            f"{category} {len(category_values[category])}"
            for category in MEASUREMENT_CATEGORIES
        )
    )

    print("\nSOURCE SUMMARIES (ordered by test-source label)")
    print(f"{'TEST SOURCE':<15} {'READINGS':>9} {'CATEGORIES':>11}")
    print("-" * 38)
    for source in sorted(source_values):
        print(
            f"{source:<15} {len(source_values[source]):>9} "
            f"{len({record.category for record in records if record.test_source == source}):>11}"
        )

    print("\nCATEGORY SUMMARIES (in defined category order)")
    print(f"{'CATEGORY':<15} {'READINGS':>9} {'AVERAGE':>10} {'MIN':>8} {'MAX':>8}")
    print("-" * 54)
    for category in MEASUREMENT_CATEGORIES:
        average, minimum, maximum = summarize_values(category_values[category])
        print(
            f"{category:<15} {len(category_values[category]):>9} "
            f"{average:>10.2f} {minimum:>8} {maximum:>8}"
        )

    print("\nOVERALL TEST DATA SUMMARY")
    print(f"Measurement records: {len(records)}")
    print(f"Distinct test sources: {len(distinct_sources)}")
    print(f"Distinct measurement categories: {len(distinct_categories)}")
    print(f"Distinct source/category pairs: {len(pair_counts)}")
    print(f"Repeated source/category pairs: {len(repeated_pairs)}")
    print(
        "Numerical statistics are summarized by category; cross-category "
        "averages and ranges are omitted because measurement scales differ."
    )


if __name__ == "__main__":
    main()
