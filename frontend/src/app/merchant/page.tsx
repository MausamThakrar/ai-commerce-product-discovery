"use client";

import {
  ChangeEvent,
  FormEvent,
  useEffect,
  useState,
} from "react";

import {
  getCatalogStatus,
  importCatalog,
  resetCatalog,
  updateSearchSettings,
} from "@/lib/api";

import type {
  CatalogSource,
  CatalogStatus,
  SearchSettings,
} from "@/types/commerce";


export default function MerchantPage() {
  const [
    status,
    setStatus,
  ] = useState<CatalogStatus | null>(
    null
  );

  const [
    settings,
    setSettings,
  ] = useState<SearchSettings | null>(
    null
  );

  const [source, setSource] =
    useState<CatalogSource>(
      "generic-json"
    );

  const [file, setFile] =
    useState<File | null>(null);

  const [loading, setLoading] =
    useState(true);

  const [importing, setImporting] =
    useState(false);

  const [saving, setSaving] =
    useState(false);

  const [message, setMessage] =
    useState("");

  const [error, setError] =
    useState("");


  async function loadStatus() {
    try {
      setError("");

      const catalog =
        await getCatalogStatus();

      setStatus(catalog);
      setSettings(
        catalog.settings
      );
    } catch {
      setError(
        "Could not load merchant configuration."
      );
    } finally {
      setLoading(false);
    }
  }


  useEffect(() => {
    loadStatus();
  }, []);


  function handleFileChange(
    event: ChangeEvent<HTMLInputElement>
  ) {
    const selected =
      event.target.files?.[0] ??
      null;

    setFile(selected);
  }


  async function handleImport(
    event: FormEvent<HTMLFormElement>
  ) {
    event.preventDefault();

    if (!file) {
      setError(
        "Select a catalog file first."
      );
      return;
    }

    setImporting(true);
    setError("");
    setMessage("");

    try {
      const text =
        await file.text();

      const catalog =
        await importCatalog(
          source,
          text
        );

      setStatus(catalog);
      setSettings(
        catalog.settings
      );

      setMessage(
        `Imported ${catalog.product_count} products successfully.`
      );

      setFile(null);
    } catch (error) {
      setError(
        error instanceof Error
          ? error.message
          : "Catalog import failed."
      );
    } finally {
      setImporting(false);
    }
  }


  async function handleReset() {
    setImporting(true);
    setError("");
    setMessage("");

    try {
      const catalog =
        await resetCatalog();

      setStatus(catalog);
      setSettings(
        catalog.settings
      );

      setMessage(
        "Demo catalog restored."
      );
    } catch {
      setError(
        "Could not restore the demo catalog."
      );
    } finally {
      setImporting(false);
    }
  }


  async function handleSettingsSave(
    event: FormEvent<HTMLFormElement>
  ) {
    event.preventDefault();

    if (!settings) {
      return;
    }

    setSaving(true);
    setError("");
    setMessage("");

    try {
      const updated =
        await updateSearchSettings(
          settings
        );

      setSettings(updated);

      setStatus((current) =>
        current
          ? {
              ...current,
              settings: updated,
            }
          : current
      );

      setMessage(
        "Search settings updated."
      );
    } catch (error) {
      setError(
        error instanceof Error
          ? error.message
          : "Could not save settings."
      );
    } finally {
      setSaving(false);
    }
  }


  if (loading) {
    return (
      <main className="merchantPage">
        <p>
          Loading merchant configuration...
        </p>
      </main>
    );
  }


  return (
    <main className="merchantPage">
      <header className="merchantHeader">
        <div>
          <span className="sectionLabel">
            MERCHANT TOOLS
          </span>

          <h1>
            Catalog & Discovery
          </h1>

          <p>
            Connect product data and
            configure how the discovery
            engine behaves.
          </p>
        </div>

        <a
          className="merchantBackLink"
          href="/"
        >
          ← Storefront
        </a>
      </header>


      {error && (
        <div className="merchantNotice errorMessage">
          {error}
        </div>
      )}

      {message && (
        <div className="merchantNotice successMessage">
          {message}
        </div>
      )}


      {status && (
        <section className="merchantSection">
          <div className="merchantSectionHeader">
            <div>
              <span className="sectionLabel">
                CURRENT CATALOG
              </span>

              <h2>
                {status.product_count} products
              </h2>
            </div>

            <span className="sourceBadge">
              {status.source}
            </span>
          </div>

          <div className="statsGrid">
            <Stat
              label="Products"
              value={
                status.product_count
              }
            />

            <Stat
              label="In stock"
              value={
                status.products_in_stock
              }
            />

            <Stat
              label="Categories"
              value={
                status.category_count
              }
            />

            <Stat
              label="Brands"
              value={
                status.brand_count
              }
            />

            <Stat
              label="Variants"
              value={
                status.variant_count
              }
            />
          </div>

          <div className="catalogMetadata">
            <div>
              <strong>
                Categories
              </strong>

              <div className="metadataChips">
                {status.categories.map(
                  (category) => (
                    <span
                      key={category}
                    >
                      {category}
                    </span>
                  )
                )}
              </div>
            </div>

            <div>
              <strong>
                Brands
              </strong>

              <div className="metadataChips">
                {status.brands.map(
                  (brand) => (
                    <span key={brand}>
                      {brand}
                    </span>
                  )
                )}
              </div>
            </div>
          </div>
        </section>
      )}


      <section className="merchantGrid">
        <form
          className="merchantSection"
          onSubmit={handleImport}
        >
          <span className="sectionLabel">
            IMPORT CATALOG
          </span>

          <h2>
            Replace product data
          </h2>

          <p>
            Imported products are converted
            into the common catalog model
            and the search indexes are
            rebuilt automatically.
          </p>

          <label className="merchantField">
            <span>
              Source format
            </span>

            <select
              value={source}
              onChange={(event) =>
                setSource(
                  event.target
                    .value as CatalogSource
                )
              }
            >
              <option value="generic-json">
                Generic JSON
              </option>

              <option value="generic-csv">
                Generic CSV
              </option>

              <option value="shopify">
                Shopify JSON
              </option>
            </select>
          </label>

          <label className="merchantField">
            <span>
              Catalog file
            </span>

            <input
              type="file"
              accept={
                source ===
                "generic-csv"
                  ? ".csv,text/csv"
                  : ".json,application/json"
              }
              onChange={
                handleFileChange
              }
            />
          </label>

          {file && (
            <p className="selectedFile">
              Selected: {file.name}
            </p>
          )}

          <button
            className="merchantPrimaryButton"
            type="submit"
            disabled={importing}
          >
            {importing
              ? "Building search index..."
              : "Import catalog"}
          </button>

          <button
            className="merchantSecondaryButton"
            type="button"
            onClick={handleReset}
            disabled={importing}
          >
            Restore demo catalog
          </button>
        </form>


        {settings && (
          <form
            className="merchantSection"
            onSubmit={
              handleSettingsSave
            }
          >
            <span className="sectionLabel">
              SEARCH CONFIGURATION
            </span>

            <h2>
              Discovery behavior
            </h2>

            <label className="merchantField">
              <span>
                Maximum recommendations
              </span>

              <input
                type="number"
                min="1"
                max="20"
                value={
                  settings
                    .max_recommendations
                }
                onChange={(event) =>
                  setSettings({
                    ...settings,
                    max_recommendations:
                      Number(
                        event.target
                          .value
                      ),
                  })
                }
              />
            </label>

            <label className="merchantField">
              <span>
                Semantic weight
              </span>

              <input
                type="number"
                min="0"
                max="1"
                step="0.05"
                value={
                  settings
                    .semantic_weight
                }
                onChange={(event) =>
                  setSettings({
                    ...settings,
                    semantic_weight:
                      Number(
                        event.target
                          .value
                      ),
                  })
                }
              />
            </label>

            <label className="merchantField">
              <span>
                Keyword weight
              </span>

              <input
                type="number"
                min="0"
                max="1"
                step="0.05"
                value={
                  settings
                    .keyword_weight
                }
                onChange={(event) =>
                  setSettings({
                    ...settings,
                    keyword_weight:
                      Number(
                        event.target
                          .value
                      ),
                  })
                }
              />
            </label>

            <label className="merchantToggle">
              <input
                type="checkbox"
                checked={
                  settings
                    .hide_unavailable
                }
                onChange={(event) =>
                  setSettings({
                    ...settings,
                    hide_unavailable:
                      event.target
                        .checked,
                  })
                }
              />

              <span>
                Hide unavailable products
              </span>
            </label>

            <button
              className="merchantPrimaryButton"
              type="submit"
              disabled={saving}
            >
              {saving
                ? "Saving..."
                : "Save configuration"}
            </button>
          </form>
        )}
      </section>


      <section className="merchantSection merchantArchitecture">
        <span className="sectionLabel">
          CATALOG PIPELINE
        </span>

        <h2>
          One engine, multiple data sources
        </h2>

        <div className="pipeline">
          <div>
            JSON
          </div>

          <div>
            CSV
          </div>

          <div>
            Shopify
          </div>

          <span>→</span>

          <div>
            Common product model
          </div>

          <span>→</span>

          <div>
            AI discovery engine
          </div>

          <span>→</span>

          <div>
            Storefront
          </div>
        </div>
      </section>
    </main>
  );
}


function Stat({
  label,
  value,
}: {
  label: string;
  value: number;
}) {
  return (
    <div className="statCard">
      <strong>
        {value}
      </strong>

      <span>
        {label}
      </span>
    </div>
  );
}