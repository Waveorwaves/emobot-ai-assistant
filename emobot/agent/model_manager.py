"""
多模型管理器
支持 OpenAI GPT 和 Google Gemini 的自动切换
"""

import os
import logging
from typing import Optional, Dict, Any, List, Union
from smolagents import OpenAIServerModel, ToolCallingAgent

# 条件导入 google.generativeai
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    genai = None

logger = logging.getLogger(__name__)

class ModelManager:
    """多模型管理器，支持自动切换和故障转移"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.current_model = None
        self.model_configs = self._load_model_configs()
        # 根据指定的模型调整优先级
        self.fallback_order = ["gemini", "openai", "local"]
        
    def _load_model_configs(self) -> Dict[str, Dict[str, Any]]:
        """加载模型配置"""
        configs = {
            "openai": {
                "enabled": bool(os.getenv("OPENAI_API_KEY")),
                "api_key": os.getenv("OPENAI_API_KEY"),
                "models": ["gpt-4", "gpt-3.5-turbo", "gpt-4o"],
                "default_model": "gpt-4"
            },
            "gemini": {
                "enabled": bool(os.getenv("GOOGLE_API_KEY")),
                "api_key": os.getenv("GOOGLE_API_KEY"),
                "models": ["gemini-2.5-flash", "gemini-2.0-flash", "gemini-flash-latest"],
                "default_model": "gemini-2.5-flash"
            },
            "local": {
                "enabled": True,  # 本地模型总是可用的
                "models": ["local"],
                "default_model": "local"
            }
        }
        return configs
    
    def get_available_models(self) -> List[str]:
        """获取可用的模型列表"""
        available = []
        for provider, config in self.model_configs.items():
            if config["enabled"]:
                available.extend(config["models"])
        return available
    
    def create_model(self, model_id: Optional[str] = None) -> Optional[Any]:
        """创建模型实例，支持自动故障转移"""
        
        # 如果没有指定模型，使用默认模型
        if not model_id:
            model_id = os.getenv("DEFAULT_MODEL", "gpt-4")
        
        # 首先尝试创建指定的模型
        if model_id:
            # 确定指定模型属于哪个提供商
            target_provider = None
            for provider in self.fallback_order:
                if self._is_model_from_provider(model_id, provider):
                    target_provider = provider
                    break
            
            if target_provider and target_provider in self.model_configs:
                config = self.model_configs[target_provider]
                if config["enabled"]:
                    try:
                        model = self._create_provider_model(target_provider, model_id)
                        if model:
                            self.current_model = model
                            self.logger.info(f"Successfully created specified {target_provider} model: {model_id}")
                            return model
                    except Exception as e:
                        self.logger.warning(f"创建指定的 {target_provider} 模型失败: {e}")
        
        # 如果指定模型失败，按优先级尝试其他模型
        for provider in self.fallback_order:
            if provider not in self.model_configs:
                continue
                
            config = self.model_configs[provider]
            if not config["enabled"]:
                continue
            
            # 检查模型是否属于当前提供商
            if self._is_model_from_provider(model_id, provider):
                try:
                    model = self._create_provider_model(provider, model_id)
                    if model:
                        self.current_model = model
                        self.logger.info(f"成功创建 {provider} 模型: {model_id}")
                        return model
                except Exception as e:
                    self.logger.warning(f"创建 {provider} 模型失败: {e}")
                    continue
        
        # 如果所有模型都失败，尝试使用默认模型
        for provider in self.fallback_order:
            if provider not in self.model_configs:
                continue
                
            config = self.model_configs[provider]
            if not config["enabled"]:
                continue
            
            try:
                default_model_id = config["default_model"]
                model = self._create_provider_model(provider, default_model_id)
                if model:
                    self.current_model = model
                    self.logger.info(f"使用默认 {provider} 模型: {default_model_id}")
                    return model
            except Exception as e:
                self.logger.warning(f"创建默认 {provider} 模型失败: {e}")
                continue
        
        self.logger.error("所有模型都无法创建")
        return None
    
    def _is_model_from_provider(self, model_id: str, provider: str) -> bool:
        """判断模型是否属于指定提供商"""
        if provider == "openai":
            return model_id.startswith("gpt-")
        elif provider == "gemini":
            return model_id.startswith("gemini-")
        elif provider == "local":
            return model_id == "local"
        return False
    
    def _create_provider_model(self, provider: str, model_id: str) -> Optional[Any]:
        """创建指定提供商的模型"""
        if provider == "openai":
            return self._create_openai_model(model_id)
        elif provider == "gemini":
            return self._create_gemini_model(model_id)
        elif provider == "local":
            return self._create_local_model(model_id)
        return None
    
    def _create_openai_model(self, model_id: str) -> Optional[Any]:
        """创建 OpenAI 模型"""
        try:
            api_key = self.model_configs["openai"]["api_key"]
            if not api_key or api_key == "YOUR_ACTUAL_API_KEY_HERE":
                raise ValueError("OpenAI API 密钥未配置")
            
            # 创建 OpenAI 模型
            model = OpenAIServerModel(
                model_id=model_id,  # 修正参数名
                api_key=api_key,
                temperature=float(os.getenv("MODEL_TEMPERATURE", "0.7")),
                max_tokens=int(os.getenv("MAX_TOKENS", "2000"))
            )
            
            # 测试模型连接 - 使用正确的格式
            from smolagents import ChatMessage
            test_messages = [ChatMessage(role="user", content="测试连接")]
            test_response = model.generate(test_messages)
            if test_response:
                return model
                
        except Exception as e:
            self.logger.error(f"创建 OpenAI 模型失败: {e}")
            return None
    
    def _create_gemini_model(self, model_id: str) -> Optional[Any]:
        """创建 Google Gemini 模型"""
        try:
            if not GEMINI_AVAILABLE:
                self.logger.warning("google-generativeai 未安装，跳过 Gemini 模型")
                return None
                
            api_key = self.model_configs["gemini"]["api_key"]
            if not api_key:
                raise ValueError("Google API 密钥未配置")
            
            # 配置 Google API
            if genai:
                genai.configure(api_key=api_key)  # type: ignore
            
            # 创建 Gemini 模型包装器
            class GeminiModelWrapper:
                def __init__(self, model_name: str):
                    if genai:
                        self.gemini_model = genai.GenerativeModel(model_name)  # type: ignore
                    else:
                        raise ImportError("google.generativeai 未安装")
                    self.model_name = model_name
                    self.last_request_time = 0
                    self.min_interval = 2  # 最小请求间隔（秒）
                    # 添加 model 属性以兼容 smolagents
                    self.model = self  # 指向自身，用于 smolagents 识别
                
                def generate(self, prompt, **kwargs) -> str:
                    import time
                    
                    # 处理 List[ChatMessage] 类型
                    if isinstance(prompt, list):
                        # 构建完整的对话历史，而不是只取最后一个消息
                        conversation_parts = []
                        for msg in prompt:
                            if hasattr(msg, 'role') and hasattr(msg, 'content'):
                                role = getattr(msg, 'role', 'unknown')
                                if isinstance(msg.content, list) and len(msg.content) > 0:
                                    content = msg.content[0].get('text', str(msg.content))
                                else:
                                    content = str(msg.content)
                                conversation_parts.append(f"{role}: {content}")
                            else:
                                conversation_parts.append(str(msg))
                        
                        # 如果有多个消息，组合成完整对话
                        if len(conversation_parts) > 1:
                            prompt_text = "\n".join(conversation_parts)
                        else:
                            prompt_text = conversation_parts[0] if conversation_parts else str(prompt)
                            
                    elif hasattr(prompt, 'role') and getattr(prompt, 'role', None) == 'user':
                        # 单个 ChatMessage 对象
                        if hasattr(prompt, 'content') and isinstance(prompt.content, list) and len(prompt.content) > 0:
                            prompt_text = prompt.content[0].get('text', '')
                        else:
                            prompt_text = str(prompt)
                    else:
                        # 其他类型直接转换为字符串
                        prompt_text = str(prompt)

                    current_time = time.time()
                    time_since_last = current_time - self.last_request_time
                    if time_since_last < self.min_interval:
                        sleep_time = self.min_interval - time_since_last
                        time.sleep(sleep_time)
                    try:
                        response = self.gemini_model.generate_content(prompt_text)
                        self.last_request_time = time.time()
                        # 正确访问 Gemini API 响应的文本内容
                        try:
                            # 直接使用 text 属性
                            if hasattr(response, 'text'):
                                return response.text
                            
                            # 备用方法：使用 getattr 来安全访问属性
                            result = getattr(response, 'result', None)
                            if result:
                                candidates = getattr(result, 'candidates', [])
                                if candidates and len(candidates) > 0:
                                    candidate = candidates[0]
                                    content = getattr(candidate, 'content', None)
                                    if content:
                                        parts = getattr(content, 'parts', [])
                                        if parts and len(parts) > 0:
                                            text_content = getattr(parts[0], 'text', '')
                                            # 返回 smolagents 期望的格式
                                            return text_content
                            # 如果无法通过标准路径访问，尝试其他方法
                            return "无法解析响应内容"
                        except Exception:
                            # 如果访问失败，返回错误信息
                            return "响应解析失败"
                    except Exception as e:
                        error_msg = str(e)
                        if "429" in error_msg or "quota" in error_msg.lower():
                            self.min_interval = max(self.min_interval * 2, 10)
                            raise Exception(f"Gemini API 配额限制: {error_msg}")
                        else:
                            raise Exception(f"Gemini 生成失败: {error_msg}")
                
                def __str__(self):
                    return f"GeminiModel({self.model_name})"
            
            # 测试模型连接
            model = GeminiModelWrapper(model_id)
            try:
                test_response = model.generate("测试连接")
                if test_response:
                    return model
            except Exception as e:
                self.logger.warning(f"Gemini 模型测试失败: {e}")
                return None
                
        except Exception as e:
            self.logger.error(f"创建 Gemini 模型失败: {e}")
            return None
    
    def _create_local_model(self, model_id: str) -> Optional[Any]:
        """创建本地模型（简化实现）"""
        try:
            # 这里可以集成本地模型，如 Ollama、LM Studio 等
            # 目前返回一个简单的回显模型用于测试
            
            class LocalModelWrapper:
                def __init__(self):
                    self.name = "local-echo"
                
                def generate(self, prompt: str) -> str:
                    return f"本地模型回复: {prompt}"
                
                def __str__(self):
                    return f"LocalModel({self.name})"
            
            return LocalModelWrapper()
            
        except Exception as e:
            self.logger.error(f"创建本地模型失败: {e}")
            return None
    
    def create_agent(self, model, tools: List[Any], system_prompt: str):
        """Create tool calling agent"""
        try:
            # 对于 OpenAI 模型，直接使用 smolagents 的 ToolCallingAgent
            if (hasattr(model, 'generate') and 
                hasattr(model, 'model') and 
                hasattr(model.model, 'startswith') and 
                model.model.startswith('gpt')):
                agent = ToolCallingAgent(
                    model=model,
                    tools=tools
                )
                return agent
            else:
                # 对于其他模型，创建自定义代理
                return self._create_custom_agent(model, tools, system_prompt)
                
        except Exception as e:
            self.logger.error(f"创建代理失败: {e}")
            return None
    
    def _create_custom_agent(self, model, tools: List[Any], system_prompt: str):
        """创建自定义代理（用于非 OpenAI 模型）"""
        class CustomAgent:
            def __init__(self, model, tools, system_prompt):
                self.model = model
                self.tools = tools
                self.system_prompt = system_prompt
            
            def run(self, query: str):
                # Simplified implementation, should include tool calling logic
                full_prompt = f"{self.system_prompt}\n\nUser Query: {query}"
                response = self.model.generate(full_prompt)
                
                # 返回一个类似 smolagents 响应的对象
                class ResponseWrapper:
                    def __init__(self, content):
                        self.content = content
                    
                    def __str__(self):
                        return self.content
                
                return ResponseWrapper(response)
        
        return CustomAgent(model, tools, system_prompt)
    
    def get_model_status(self) -> Dict[str, Any]:
        """获取模型状态信息"""
        status = {
            "current_model": str(self.current_model) if self.current_model else None,
            "available_providers": [],
            "provider_status": {}
        }
        
        for provider, config in self.model_configs.items():
            status["provider_status"][provider] = {
                "enabled": config["enabled"],
                "models": config["models"],
                "default_model": config.get("default_model")
            }
            if config["enabled"]:
                status["available_providers"].append(provider)
        
        return status 

    def create_gemini_model(self, model_id: str = "gemini-1.5-flash") -> Any:
        """Create Gemini model with fallback options"""
        try:
            import google.generativeai as genai
            
            # Set API key
            api_key = os.getenv("GOOGLE_API_KEY")
            if not api_key:
                raise Exception("GOOGLE_API_KEY not found in environment variables")
            
            genai.configure(api_key=api_key)
            
            # Available Gemini models with their free quotas
            gemini_models = {
                "gemini-1.5-flash": {
                    "model": "gemini-1.5-flash",
                    "free_quota": 50,
                    "description": "Fastest, cheapest model"
                },
                "gemini-1.5-pro": {
                    "model": "gemini-1.5-pro", 
                    "free_quota": 150,
                    "description": "Better reasoning, higher quota"
                },
                "gemini-1.0-pro": {
                    "model": "gemini-1.0-pro",
                    "free_quota": 150,
                    "description": "Stable, reliable performance"
                }
            }
            
            # Try the requested model first
            if model_id in gemini_models:
                try:
                    model = genai.GenerativeModel(gemini_models[model_id]["model"])
                    self.logger.info(f"Successfully created {model_id} model (Free quota: {gemini_models[model_id]['free_quota']} requests/day)")
                    return model
                except Exception as e:
                    self.logger.warning(f"Failed to create {model_id}: {e}")
            
            # Fallback to other models if requested model fails
            for fallback_id, fallback_info in gemini_models.items():
                if fallback_id != model_id:
                    try:
                        model = genai.GenerativeModel(fallback_info["model"])
                        self.logger.info(f"Fallback: Created {fallback_id} model (Free quota: {fallback_info['free_quota']} requests/day)")
                        return model
                    except Exception as e:
                        self.logger.warning(f"Fallback {fallback_id} also failed: {e}")
                        continue
            
            raise Exception("All Gemini models failed to initialize")
            
        except ImportError:
            raise Exception("google-generativeai package not installed")
        except Exception as e:
            raise Exception(f"Failed to create Gemini model: {e}") 