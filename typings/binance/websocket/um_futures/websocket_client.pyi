"""
This type stub file was generated by pyright.
"""

from binance.websocket.websocket_client import BinanceWebsocketClient

class UMFuturesWebsocketClient(BinanceWebsocketClient):
    def __init__(self, stream_url=...) -> None:
        ...
    
    def agg_trade(self, symbol: str, id: int, callback, **kwargs): # -> None:
        """Aggregate Trade Streams

        The Aggregate Trade Streams push market trade information that is aggregated for a single taker order every 100 milliseconds.
        Only market trades will be aggregated, which means the insurance fund trades and ADL trades won't be aggregated.

        Stream Name: <symbol>@aggTrade

        https://binance-docs.github.io/apidocs/futures/en/#aggregate-trade-streams

        Update Speed: 100ms
        """
        ...
    
    def mark_price(self, symbol: str, id: int, speed: int, callback, **kwargs): # -> None:
        """Mark Price Streams

        Mark price and funding rate for all symbols pushed every 3 seconds or every second.

        Stream Name: <symbol>@markPrice or <symbol>@markPrice@1s

        https://binance-docs.github.io/apidocs/futures/en/#mark-price-stream

        Update Speed: 3000ms or 1000ms
        """
        ...
    
    def kline(self, symbol: str, id: int, interval: str, callback, **kwargs): # -> None:
        """Kline/Candlestick Streams

        The Kline/Candlestick Stream push updates to the current klines/candlestick every 250 milliseconds (if existing)

        Stream Name: <symbol>@kline_<interval>

        https://binance-docs.github.io/apidocs/futures/en/#kline-candlestick-streams

        interval:
        m -> minutes; h -> hours; d -> days; w -> weeks; M -> months

        - 1m
        - 3m
        - 5m
        - 15m
        - 30m
        - 1h
        - 2h
        - 4h
        - 6h
        - 8h
        - 12h
        - 1d
        - 3d
        - 1w
        - 1M

        Update Speed: 250ms
        """
        ...
    
    def continuous_kline(self, pair: str, id: int, contractType: str, interval: str, callback, **kwargs): # -> None:
        """Continuous Kline/Candlestick Streams

        The Kline/Candlestick Stream push updates to Kline/candlestick bars for a specific contract type. every 250 milliseconds

        Stream Name: <pair>_<contractType>@continuousKline_<interval>

        https://binance-docs.github.io/apidocs/futures/en/#continuous-contract-kline-candlestick-streams

        interval:
        m -> minutes; h -> hours; d -> days; w -> weeks; M -> months

        - 1m
        - 3m
        - 5m
        - 15m
        - 30m
        - 1h
        - 2h
        - 4h
        - 6h
        - 8h
        - 12h
        - 1d
        - 3d
        - 1w
        - 1M

        Update Speed: 250ms
        """
        ...
    
    def mini_ticker(self, id: int, callback, symbol=..., **kwargs): # -> None:
        """Individual symbol or all symbols mini ticker

        24hr rolling window mini-ticker statistics.
        These are NOT the statistics of the UTC day, but a 24hr rolling window for the previous 24hrs

        Stream Name: <symbol>@miniTicker or
        Stream Name: !miniTicker@arr

        https://binance-docs.github.io/apidocs/futures/en/#individual-symbol-mini-ticker-stream
        https://binance-docs.github.io/apidocs/futures/en/#individual-symbol-ticker-streams

        Update Speed: 500ms for individual symbol, 1000ms for all market symbols
        """
        ...
    
    def ticker(self, id: int, callback, symbol=..., **kwargs): # -> None:
        """Individual symbol or all symbols ticker

        24hr rolling window ticker statistics for a single symbol.
        These are NOT the statistics of the UTC day, but a 24hr rolling window from requestTime to 24hrs before.

        Stream Name: <symbol>@ticker or
        Stream Name: !ticker@arr

        https://binance-docs.github.io/apidocs/futures/en/#individual-symbol-ticker-streams
        https://binance-docs.github.io/apidocs/futures/en/#all-market-tickers-streams

        Update Speed: 500ms for individual symbol, 1000ms for all market symbols
        """
        ...
    
    def book_ticker(self, id: int, callback, symbol=..., **kwargs): # -> None:
        """Individual symbol or all book ticker

        Pushes any update to the best bid or ask's price or quantity in real-time for a specified symbol.

        Stream Name: <symbol>@bookTicker or
        Stream Name: !bookTicker

        https://binance-docs.github.io/apidocs/futures/en/#individual-symbol-book-ticker-streams
        https://binance-docs.github.io/apidocs/futures/en/#all-book-tickers-stream

        Update Speed: Real-time
        """
        ...
    
    def liquidation_order(self, id: int, callback, symbol=..., **kwargs): # -> None:
        """The Liquidation Order Snapshot Streams push force liquidation order information for specific symbol.
        The All Liquidation Order Snapshot Streams push force liquidation order information for all symbols in the market.

        For each symbol，only the latest one liquidation order within 1000ms will be pushed as the snapshot. If no liquidation happens in the interval of 1000ms, no stream will be pushed.

        Stream Name: <symbol>@forceOrder or
        Stream Name: !forceOrder@arr

        https://binance-docs.github.io/apidocs/futures/en/#liquidation-order-streams
        https://binance-docs.github.io/apidocs/futures/en/#all-market-liquidation-order-streams

        Update Speed: 1000ms
        """
        ...
    
    def partial_book_depth(self, symbol: str, id: int, level, speed, callback, **kwargs): # -> None:
        """Partial Book Depth Streams

        Top bids and asks, Valid are 5, 10, or 20.

        Stream Names: <symbol>@depth<levels> OR <symbol>@depth<levels>@500ms OR <symbol>@depth<levels>@100ms

        https://binance-docs.github.io/apidocs/futures/en/#partial-book-depth-streams

        Update Speed: 250ms, 500ms or 100ms
        """
        ...
    
    def diff_book_depth(self, symbol: str, id: int, speed, callback, **kwargs): # -> None:
        """Diff. Depth Stream
        Order book price and quantity depth updates used to locally manage an order book.

        Stream Name: <symbol>@depth OR <symbol>@depth@500ms OR<symbol>@depth@100ms

        https://binance-docs.github.io/apidocs/futures/en/#diff-book-depth-streams

        Update Speed: 250ms, 500ms or 100ms
        """
        ...
    
    def composite_index(self, symbol: str, id: int, callback, **kwargs): # -> None:
        """Composite Index Info Stream
        Composite index information for index symbols pushed every second.

        Stream Name: <symbol>@compositeIndex

        https://binance-docs.github.io/apidocs/futures/en/#composite-index-symbol-information-streams

        Update Speed: 1000ms
        """
        ...
    
    def user_data(self, listen_key: str, id: int, callback, **kwargs): # -> None:
        """listen to user data by provided listenkey"""
        ...
    


