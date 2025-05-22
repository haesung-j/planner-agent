import os
import logging

from abc import ABC, abstractmethod
from typing import Optional, Union


class BaseNode(ABC):
    """
    langgraph에서 사용할 기본 노드 클래스입니다.

    모든 노드는 이 클래스를 상속받아 run 메서드를 구현해야 합니다.
    노드는 입력 상태를 받아 처리한 후 출력 상태를 반환합니다.

    Attributes:
        name (str): 노드의 이름
        verbose (bool): 상세 로깅 활성화 여부
        logger (logging.Logger): 로깅을 위한 로거 인스턴스
    """

    def __init__(
        self, name: Optional[str] = None, verbose: Union[bool, str] = False, **kwargs
    ):
        """
        노드 초기화

        Args:
            name (Optional[str]): 노드 이름, 기본값은 클래스 이름
            verbose (Union[bool, str]): 로깅 수준 설정 ("info", "debug" 또는 False)
            **kwargs: 추가 매개변수
        """
        self.name = name or self.__class__.__name__
        self.verbose = verbose

        # 로거 설정
        self.logger = logging.getLogger(f"{self.name}")

        # 로깅 레벨 설정
        self._configure_logger()

    def _configure_logger(self) -> None:
        """로거 설정을 구성합니다."""
        # 기존 핸들러 제거
        for handler in self.logger.handlers[:]:
            self.logger.removeHandler(handler)

        # verbose가 False면 로깅 비활성화
        if self.verbose is False:
            self.logger.setLevel(logging.CRITICAL + 1)  # 로깅 비활성화
            return

        # 핸들러 생성
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            "%(asctime)s - [%(levelname)s] %(name)s\t%(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

        # 로깅 레벨 설정
        if self.verbose == "debug":
            self.logger.setLevel(logging.DEBUG)
        elif self.verbose == "info":
            self.logger.setLevel(logging.INFO)
        else:
            # 기본값 또는 알 수 없는 값의 경우 INFO 레벨 사용
            self.logger.setLevel(logging.INFO)

    def log(self, message: str, level: str = "info", **kwargs) -> None:
        """
        지정된 레벨로 메시지를 로깅합니다.

        Args:
            message (str): 로깅할 메시지
            level (str): 로깅 레벨 ('debug', 'info', 'warning', 'error', 'critical')
            **kwargs: 추가 로깅 정보
        """
        # verbose가 False면 로깅하지 않음
        if self.verbose is False:
            return

        log_func = getattr(self.logger, level.lower(), self.logger.info)

        # 기본 메시지 로깅
        log_func(f"{message}")

    @abstractmethod
    async def arun(self, state):
        """
        노드의 비동기 실행 로직을 구현합니다.

        Args:
            state (SummaryState): 입력 상태 데이터

        Returns:
            SummaryState: 처리된 출력 상태 데이터
        """
        pass

    async def __call__(self, state):
        """
        노드를 함수처럼 호출할 수 있게 해주는 메서드입니다.

        Args:
            state (SummaryState): 입력 상태 데이터

        Returns:
            SummaryState: 처리된 출력 상태 데이터
        """
        self.log("Start running a node", "info")
        result = await self.arun(state)
        self.log("Finish running the node", "info")
        return result
