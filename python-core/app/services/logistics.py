"""物流服务，用于查询订单物流信息。

该服务处理物流查询，包括订单状态获取、
物流轨迹和预计送达时间计算。
"""
from datetime import datetime
from typing import Optional

from app.models import (
    LogisticsInfo,
    Order,
    OrderStatus,
    TrackingEvent,
)
from app.repositories.base import LogisticsRepository, OrderRepository


class LogisticsService:
    """处理物流相关操作的服务。"""

    def __init__(
        self,
        order_repository: OrderRepository,
        logistics_repository: LogisticsRepository,
    ):
        """初始化物流服务。
        
        Args:
            order_repository: 订单数据访问的仓库。
            logistics_repository: 物流数据访问的仓库。
        """
        self.order_repository = order_repository
        self.logistics_repository = logistics_repository

    def get_logistics_info(self, order_id: str) -> Optional[LogisticsInfo]:
        """获取订单的完整物流信息。
        
        Args:
            order_id: 要查询的订单ID。
            
        Returns:
            如果找到订单返回LogisticsInfo，否则返回None。
        """
        # 获取订单状态
        order = self.order_repository.get_by_id(order_id)
        if not order:
            return None
        
        # 获取物流轨迹（最近3条）
        tracking_events = self._get_tracking_history(order_id)
        
        # 获取预计送达时间
        estimated_delivery = self._calculate_estimated_delivery(order, order_id)
        
        # 从物流轨迹或订单状态获取最新状态
        latest_status = self._get_latest_status(order, tracking_events)
        
        return LogisticsInfo(
            order_id=order_id,
            status=order.status,
            latest_status=latest_status,
            estimated_delivery=estimated_delivery,
            tracking_history=tracking_events,
        )

    def _get_tracking_history(self, order_id: str) -> list[TrackingEvent]:
        """获取订单的物流轨迹（最近3条）。
        
        Args:
            order_id: 要查询的订单ID。
            
        Returns:
            物流事件列表，最新的在前。
        """
        return self.logistics_repository.get_tracking(order_id)

    def _calculate_estimated_delivery(
        self, order: Order, order_id: str
    ) -> Optional[datetime]:
        """计算或获取预计送达时间。
        
        Args:
            order: 订单对象。
            order_id: 订单ID。
            
        Returns:
            如果可用返回预计送达时间。
        """
        # 对于已发货订单，尝试从仓库获取预计送达时间
        if order.status == OrderStatus.SHIPPED:
            return self.logistics_repository.get_estimated_delivery(order_id)
        return None

    def _get_latest_status(self, order: Order, tracking_events: list[TrackingEvent]) -> str:
        """获取最新的物流状态。
        
        Args:
            order: 订单对象。
            tracking_events: 物流事件列表。
            
        Returns:
            最新状态描述。
        """
        # 如果有物流轨迹，使用最近的一条
        if tracking_events:
            return tracking_events[0].status
        
        # 回退到订单状态
        status_messages = {
            OrderStatus.PENDING: "订单待处理，尚未发货",
            OrderStatus.PROCESSING: "订单正在处理中",
            OrderStatus.SHIPPED: "订单已发货",
            OrderStatus.DELIVERED: "订单已送达",
            OrderStatus.CANCELLED: "订单已取消",
        }
        return status_messages.get(order.status, f"订单状态: {order.status.value}")