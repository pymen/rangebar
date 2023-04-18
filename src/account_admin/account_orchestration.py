import logging
from rx.subject import Subject
from rx.operators import operators as op
from src.strategies.order_client import OrderClient
from enum import Enum


class AccountUpdateEventReasonType(Enum):
    DEPOSIT = 'DEPOSIT'
    WITHDRAW = 'WITHDRAW'
    ORDER = 'ORDER'
    FUNDING_FEE = 'FUNDING_FEE'
    WITHDRAW_REJECT = 'WITHDRAW_REJECT'
    ADJUSTMENT = 'ADJUSTMENT'
    INSURANCE_CLEAR = 'INSURANCE_CLEAR'
    ADMIN_DEPOSIT = 'ADMIN_DEPOSIT'
    ADMIN_WITHDRAW = 'ADMIN_WITHDRAW'
    MARGIN_TRANSFER = 'MARGIN_TRANSFER'
    MARGIN_TYPE_CHANGE = 'MARGIN_TYPE_CHANGE'
    ASSET_TRANSFER = 'ASSET_TRANSFER'
    OPTIONS_PREMIUM_FEE = 'OPTIONS_PREMIUM_FEE'
    OPTIONS_SETTLE_PROFIT = 'OPTIONS_SETTLE_PROFIT'
    AUTO_EXCHANGE = 'AUTO_EXCHANGE'
    COIN_SWAP_DEPOSIT = 'COIN_SWAP_DEPOSIT'
    COIN_SWAP_WITHDRAW = 'COIN_SWAP_WITHDRAW'


class AccountOrchestration:
    """
    The responsibility of this to orchestrate the order cancellation, 
    in the case of a take profit or stop loss orders.
    Also in the case of impending liquidation.

    https://binance-docs.github.io/apidocs/futures/en/#position-information-v2-user_data
    """

    def __init__(self, order_client: OrderClient, account_data_stream: Subject):
        self.account_data_stream = account_data_stream

    def subscribe(self):
        self.account_data_stream.pipe(op.map(self.map_raw_payload)).subscribe()

    def map_raw_payload(self, e):
        event_type = e['e']
        if event_type == 'ACCOUNT_CONFIG_UPDATE':
            mapping = {
                "e": "event_type",
                "E": "event_time",
                "T": "transaction_time",
                "ac_s": "symbol",
                "ac_l": "leverage",
                "ai_j": "multi_assets_mode"
            }
            # there are no lists so flattening first makes sense for this one
            flat = self.flatten_dict(e)
        elif event_type == 'ACCOUNT_UPDATE':
            mapping = {
                "e": "event_type",
                "E": "event_time",
                "T": "transaction",
                "a_m": "event_reason_type",
                "a_B": "balances",
                "a_P": "position"
            }
            positions_array_item = {
                "s": "symbol",
                "pa": "position_amount",
                "ep": "entry_price",
                "cr": "pre_fee_accumulated_realized",
                "up": "unrealized_pn_l",
                "mt": "margin_type",
                "iw": "isolated_wallet",
                "ps": "position_side"
            }
            balances_array_item = {
                "a": "asset",
                "wb": "wallet_balance",
                "cw": "cross_wallet_balance",
                "bc": "balance_change_except_pnl_and_commission"
            }
            # there are no lists so flattening first makes sense for this one
            flat = self.flatten_dict(e)
        elif event_type == 'MARGIN_CALL':
            mapping = {
                "e": "event_type",
                "E": "event_time",
                "cw": "cross_wallet_balance",
                "p": "positions"
            }
            positions_array_item = {
                "s": "symbol",
                "ps": "position_side",
                "pa": "position_amount",
                "mt": "margin_type",
                "iw": "isolated_wallet",
                "mp": "mark_price",
                "up": "unrealized_pnl",
                "mm": "maintenance_margin_required"
            }
        elif event_type == 'ORDER_TRADE_UPDATE':
            mapping = {
                "e": "event_type",
                "E": "event_time",
                "T": "transaction_time",
                "o_s": "symbol",
                "o_c": "client_order_id",
                "o_S": "side",
                "o_f": "timein_force",
                "o_q": "original_quantity",
                "o_p": "original_price",
                "o_ap": "average_price",
                "o_sp": "stop_price",
                "o_x": "execution_type",
                "o_X": "order_status",
                "o_i": "order_id",
                "o_l": "order_last_filled_quantity",
                "o_z": "order_filled_accumulated_quantity",
                "o_L": "last_filled_price",
                "o_N": "commission_asset",
                "o_n": "commission",
                "o_T": "transaction_time",
                "o_t": "trade_id",
                "o_b": "bids_notional",
                "o_a": "average_price",
                "o_m": "trade_maker_side",
                "o_R": "reduce_only",
                "o_wt": "stop_price_working_type",
                "o_ot": "original_order_type",
                "o_ps": "position_side",
                "o_cp": "close_all",
                "o_AP": "activation_price",
                "o_cr": "callback_rate",
                "o_rp": "realized_profit"
            }
            # there are no lists so flattening first makes sense for this one
            flat = self.flatten_dict(e)

    def flatten_dict(self, d, parent_key='', sep='_'):
        items = []
        for k, v in d.items():
            new_key = parent_key + sep + k if parent_key else k
            if isinstance(v, dict):
                items.extend(self.flatten_dict(v, new_key, sep=sep).items())
            else:
                items.append((new_key, v))
        return dict(items)
