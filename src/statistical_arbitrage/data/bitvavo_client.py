"""
Bitvavo API client for fetching cryptocurrency market data.
"""

import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Literal

import polars as pl
from python_bitvavo_api.bitvavo import Bitvavo

from config.settings import settings


class BitvavoDataCollector:
    """
    Client for collecting historical and real-time data from Bitvavo exchange.

    Supports fetching OHLCV (Open, High, Low, Close, Volume) candle data
    for cryptocurrency pairs.
    """

    def __init__(
        self,
        api_key: str | None = None,
        api_secret: str | None = None,
    ):
        """
        Initialize Bitvavo client.

        Args:
            api_key: Bitvavo API key (optional, not needed for public data)
            api_secret: Bitvavo API secret (optional, not needed for public data)
        """
        # Use provided credentials or fall back to settings
        key = api_key or settings.bitvavo.bitvavo_api_key
        secret = api_secret or settings.bitvavo.bitvavo_api_secret

        # Initialize Bitvavo client
        self.client = Bitvavo({
            'APIKEY': key,
            'APISECRET': secret,
            'RESTURL': settings.bitvavo.bitvavo_rest_url,
            'WSURL': settings.bitvavo.bitvavo_ws_url,
        })

        self.rate_limit = settings.bitvavo.rate_limit_per_second

    def get_available_markets(self) -> pl.DataFrame:
        """
        Get all available trading markets on Bitvavo.

        Returns:
            DataFrame with market information (pair, status, min order size, etc.)
        """
        markets = self.client.markets({})
        return pl.DataFrame(markets)

    def get_candles(
        self,
        market: str,
        interval: str = "1h",
        limit: int = 1000,
        start: int | None = None,
        end: int | None = None,
    ) -> pl.DataFrame:
        """
        Fetch historical OHLCV candle data for a market.

        Args:
            market: Trading pair (e.g., 'ETH-EUR', 'BTC-EUR')
            interval: Candle interval - Options: 1m, 5m, 15m, 30m, 1h, 2h, 4h, 6h, 8h, 12h, 1d
            limit: Number of candles to fetch (max 1440)
            start: Start timestamp in milliseconds (optional)
            end: End timestamp in milliseconds (optional)

        Returns:
            DataFrame with columns: timestamp, open, high, low, close, volume
        """
        params = {'limit': limit}
        if start is not None:
            params['start'] = start
        if end is not None:
            params['end'] = end

        # Fetch candles from Bitvavo
        candles = self.client.candles(market, interval, params)

        if not candles:
            return pl.DataFrame()

        # Bitvavo returns list of lists: [timestamp, open, high, low, close, volume]
        # Convert to Polars DataFrame with named columns
        df = pl.DataFrame(
            candles,
            schema=["timestamp", "open", "high", "low", "close", "volume"],
            orient="row"
        )

        # Convert string columns to numeric types
        df = df.select([
            pl.col("timestamp").cast(pl.Int64),
            pl.col("open").cast(pl.Utf8).cast(pl.Float64),
            pl.col("high").cast(pl.Utf8).cast(pl.Float64),
            pl.col("low").cast(pl.Utf8).cast(pl.Float64),
            pl.col("close").cast(pl.Utf8).cast(pl.Float64),
            pl.col("volume").cast(pl.Utf8).cast(pl.Float64),
        ])

        # Convert timestamp from milliseconds to datetime
        df = df.with_columns([
            pl.from_epoch(pl.col("timestamp"), time_unit="ms").alias("datetime")
        ])

        # Reorder columns
        df = df.select(["datetime", "timestamp", "open", "high", "low", "close", "volume"])

        return df

    def get_candles_range(
        self,
        market: str,
        interval: str = "1h",
        start_date: datetime | None = None,
        end_date: datetime | None = None,
        days_back: int | None = None,
    ) -> pl.DataFrame:
        """
        Fetch historical candles for a date range.

        Handles pagination automatically if date range exceeds API limit.

        Args:
            market: Trading pair (e.g., 'ETH-EUR')
            interval: Candle interval
            start_date: Start date (if None, calculated from days_back)
            end_date: End date (if None, uses current time)
            days_back: Number of days to fetch backward from end_date

        Returns:
            DataFrame with OHLCV data for the entire range
        """
        # Determine date range
        if end_date is None:
            end_date = datetime.now()

        if start_date is None and days_back is not None:
            start_date = end_date - timedelta(days=days_back)
        elif start_date is None:
            raise ValueError("Must provide either start_date or days_back")

        # Convert to milliseconds
        start_ms = int(start_date.timestamp() * 1000)
        end_ms = int(end_date.timestamp() * 1000)

        # Fetch data in chunks (Bitvavo max is 1440 candles per request)
        all_candles = []
        current_start = start_ms
        max_limit = 1440

        while current_start < end_ms:
            # Fetch chunk
            df_chunk = self.get_candles(
                market=market,
                interval=interval,
                limit=max_limit,
                start=current_start,
                end=end_ms,
            )

            if df_chunk.is_empty():
                break

            all_candles.append(df_chunk)

            # Update start timestamp for next iteration
            current_start = df_chunk["timestamp"].max() + 1

            # Rate limiting
            time.sleep(1 / self.rate_limit)

        if not all_candles:
            return pl.DataFrame()

        # Concatenate all chunks
        result = pl.concat(all_candles)

        # Remove duplicates and sort
        result = result.unique(subset=["timestamp"]).sort("timestamp")

        return result

    def save_candles(
        self,
        df: pl.DataFrame,
        market: str,
        interval: str,
        format: Literal["parquet", "csv"] = "parquet",
    ) -> Path:
        """
        Save candle data to disk.

        Args:
            df: DataFrame with candle data
            market: Trading pair name
            interval: Candle interval
            format: File format ('parquet' or 'csv')

        Returns:
            Path to saved file
        """
        # Create filename
        start_date = df["datetime"].min().strftime("%Y%m%d")
        end_date = df["datetime"].max().strftime("%Y%m%d")
        filename = f"{market}_{interval}_{start_date}_{end_date}.{format}"

        # Ensure directory exists
        save_dir = settings.data.raw_data_dir
        save_dir.mkdir(parents=True, exist_ok=True)

        filepath = save_dir / filename

        # Save based on format
        if format == "parquet":
            df.write_parquet(filepath)
        elif format == "csv":
            df.write_csv(filepath)
        else:
            raise ValueError(f"Unsupported format: {format}")

        print(f"Saved {len(df)} candles to {filepath}")
        return filepath

    def load_candles(self, filepath: Path) -> pl.DataFrame:
        """
        Load candle data from disk.

        Args:
            filepath: Path to data file

        Returns:
            DataFrame with candle data
        """
        if filepath.suffix == ".parquet":
            return pl.read_parquet(filepath)
        elif filepath.suffix == ".csv":
            return pl.read_csv(filepath)
        else:
            raise ValueError(f"Unsupported file format: {filepath.suffix}")


def fetch_eth_etc_data(
    interval: str = "1h",
    days_back: int = 90,
    save: bool = True,
) -> tuple[pl.DataFrame, pl.DataFrame]:
    """
    Convenience function to fetch ETH and ETC data.

    Args:
        interval: Candle interval
        days_back: Number of days of historical data
        save: Whether to save data to disk

    Returns:
        Tuple of (ETH DataFrame, ETC DataFrame)
    """
    collector = BitvavoDataCollector()

    print(f"Fetching {days_back} days of {interval} data for ETH-EUR...")
    eth_df = collector.get_candles_range(
        market="ETH-EUR",
        interval=interval,
        days_back=days_back,
    )

    print(f"Fetching {days_back} days of {interval} data for ETC-EUR...")
    etc_df = collector.get_candles_range(
        market="ETC-EUR",
        interval=interval,
        days_back=days_back,
    )

    if save:
        collector.save_candles(eth_df, "ETH-EUR", interval)
        collector.save_candles(etc_df, "ETC-EUR", interval)

    return eth_df, etc_df
