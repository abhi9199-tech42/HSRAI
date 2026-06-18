from typing import Any, Dict, Optional

from hsrai.plugins.interfaces import CompressionPlugin, OutputPlugin, ReasoningPlugin


class PluginManager:
    def __init__(self):
        self.compression_plugins: Dict[str, CompressionPlugin] = {}
        self.reasoning_plugins: Dict[str, ReasoningPlugin] = {}
        self.output_plugins: Dict[str, OutputPlugin] = {}

        # Active plugins
        self.active_compression: Optional[str] = None
        self.active_reasoning: Optional[str] = None
        self.active_output: Optional[str] = None

    def register_compression(self, name: str, plugin: CompressionPlugin):
        self.compression_plugins[name] = plugin
        if not self.active_compression:
            self.active_compression = name

    def register_reasoning(self, name: str, plugin: ReasoningPlugin):
        self.reasoning_plugins[name] = plugin
        if not self.active_reasoning:
            self.active_reasoning = name

    def register_output(self, name: str, plugin: OutputPlugin):
        self.output_plugins[name] = plugin
        if not self.active_output:
            self.active_output = name

    def get_compression(self) -> Optional[CompressionPlugin]:
        if self.active_compression:
            return self.compression_plugins.get(self.active_compression)
        return None

    def get_reasoning(self) -> Optional[ReasoningPlugin]:
        if self.active_reasoning:
            return self.reasoning_plugins.get(self.active_reasoning)
        return None

    def get_output(self) -> Optional[OutputPlugin]:
        if self.active_output:
            return self.output_plugins.get(self.active_output)
        return None

    def initialize_all(self, config: Dict[str, Any]) -> None:
        """Initialize all registered plugins."""
        for name, plugin in self.compression_plugins.items():
            plugin_config = config.get("plugins", {}).get("compression", {}).get(name, {})
            plugin.initialize(plugin_config)

        for name, plugin in self.reasoning_plugins.items():
            plugin_config = config.get("plugins", {}).get("reasoning", {}).get(name, {})
            plugin.initialize(plugin_config)

        for name, plugin in self.output_plugins.items():
            plugin_config = config.get("plugins", {}).get("output", {}).get(name, {})
            plugin.initialize(plugin_config)

    def shutdown_all(self) -> None:
        """Shutdown all registered plugins."""
        for plugin in self.compression_plugins.values():
            plugin.shutdown()
        for plugin in self.reasoning_plugins.values():
            plugin.shutdown()
        for plugin in self.output_plugins.values():
            plugin.shutdown()
