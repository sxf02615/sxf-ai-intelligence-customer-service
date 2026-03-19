"""数据抽象层的仓库抽象接口。

该模块定义数据访问的抽象接口，
允许在模拟和真实数据源之间轻松切换。
"""
from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Optional

from app.models import Order, Ticket, TrackingEvent


class OrderRepository(ABC):
    """订单数据访问的抽象接口。"""

    @abstractmethod
    def get_by_id(self, order_id: str) -> Optional[Order]:
        """根据order_id获取订单。
        
        Args:
            order_id: 要查询的订单ID。
            
        Returns:
            如果找到返回Order，否则返回None。
        """
        pass

    @abstractmethod
    def update_status(self, order_id: str, status: str) -> bool:
        """更新订单状态。
        
        Args:
            order_id: 要更新的订单ID。
            status: 新状态。
            
        Returns:
            如果更新成功返回True，否则返回False。
        """
        pass

    @abstractmethod
    def cancel(self, order_id: str, reason: str) -> dict:
        """取消订单。
        
        Args:
            order_id: 要取消的订单ID。
            reason: 取消原因。
            
        Returns:
            包含取消结果和退款信息的字典。
        """
        pass


class LogisticsRepository(ABC):
    """物流数据访问的抽象接口。"""

    @abstractmethod
    def get_tracking(self, order_id: str) -> List[TrackingEvent]:
        """获取订单的物流轨迹事件。
        
        Args:
            order_id: 要查询的订单ID。
            
        Returns:
            物流事件列表（最多3条最近）。
        """
        pass

    @abstractmethod
    def get_estimated_delivery(self, order_id: str) -> Optional[datetime]:
        """获取订单的预计送达时间。
        
        Args:
            order_id: 要查询的订单ID。
            
        Returns:
            如果可用返回预计送达时间。
        """
        pass


class TicketRepository(ABC):
    """工单数据访问的抽象接口。"""

    @abstractmethod
    def create(self, ticket: Ticket) -> Ticket:
        """创建新工单。
        
        Args:
            ticket: 要创建的工单。
            
        Returns:
            带生成ID的已创建工单。
        """
        pass

    @abstractmethod
    def get_by_id(self, ticket_id: str) -> Optional[Ticket]:
        """根据ticket_id获取工单。
        
        Args:
            ticket_id: 要查询的工单ID。
            
        Returns:
            如果找到返回Ticket，否则返回None。
        """
        pass

    @abstractmethod
    def list_by_order(self, order_id: str) -> List[Ticket]:
        """列出订单的所有工单。
        
        Args:
            order_id: 要查询的订单ID。
            
        Returns:
            订单的工单列表。
        """
        pass