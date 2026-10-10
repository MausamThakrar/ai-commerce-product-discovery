import csv
import io

from app.models.product import Product


TRUE_VALUES = {
    "true",
    "1",
    "yes",
    "y",
}

FALSE_VALUES = {
    "false",
    "0",
    "no",
    "n",
}


def _optional_bool(
    value: str | None,
) -> bool | None:

    if value is None:
        return None

    normalized = value.strip().lower()

    if not normalized:
        return None

    if normalized in TRUE_VALUES:
        return True

    if normalized in FALSE_VALUES:
        return False

    raise ValueError(
        f"Invalid boolean value: {value}"
    )


def _split_tags(
    value: str | None,
) -> list[str]:

    if not value:
        return []

    return [
        tag.strip()
        for tag in value.split("|")
        if tag.strip()
    ]


class GenericCsvCatalogAdapter:
    """
    Imports one product per CSV row.

    Tags use the pipe character:

    outdoor|mountain|rain

    Supported structured attributes:
    color
    waterproof
    lightweight
    use_case
    """

    source_name = "generic-csv"

    required_columns = {
        "id",
        "title",
        "description",
        "category",
        "brand",
        "price",
    }

    def load(
        self,
        csv_text: str,
    ) -> list[Product]:

        reader = csv.DictReader(
            io.StringIO(csv_text)
        )

        if not reader.fieldnames:
            raise ValueError(
                "CSV contains no header."
            )

        missing_columns = (
            self.required_columns
            - set(reader.fieldnames)
        )

        if missing_columns:
            missing = ", ".join(
                sorted(missing_columns)
            )

            raise ValueError(
                "CSV is missing required "
                f"columns: {missing}"
            )

        products: list[Product] = []

        for row_number, row in enumerate(
            reader,
            start=2,
        ):
            try:
                attributes = {}

                color = (
                    row.get("color") or ""
                ).strip()

                if color:
                    attributes["color"] = color

                waterproof = _optional_bool(
                    row.get("waterproof")
                )

                if waterproof is not None:
                    attributes[
                        "waterproof"
                    ] = waterproof

                lightweight = _optional_bool(
                    row.get("lightweight")
                )

                if lightweight is not None:
                    attributes[
                        "lightweight"
                    ] = lightweight

                use_case = (
                    row.get("use_case") or ""
                ).strip()

                if use_case:
                    attributes[
                        "use_case"
                    ] = use_case

                product = Product(
                    id=row["id"].strip(),
                    title=row["title"].strip(),
                    description=(
                        row["description"].strip()
                    ),
                    category=(
                        row["category"].strip()
                    ),
                    brand=row["brand"].strip(),
                    price=float(row["price"]),
                    currency=(
                        row.get("currency")
                        or "EUR"
                    ).strip(),
                    tags=_split_tags(
                        row.get("tags")
                    ),
                    attributes=attributes,
                    inventory=int(
                        row.get("inventory")
                        or 0
                    ),
                    variants=[],
                )

            except (
                TypeError,
                ValueError,
            ) as exc:
                raise ValueError(
                    "Invalid CSV product "
                    f"at row {row_number}: "
                    f"{exc}"
                ) from exc

            products.append(product)

        if not products:
            raise ValueError(
                "CSV catalog contains "
                "no products."
            )

        return products