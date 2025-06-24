class ApiService {
  constructor() {
    const isHttps = window.location.protocol === 'https:';
    
    if (isHttps) {
      console.log('Using GitHub Codespaces');
      const currentHostname = window.location.hostname;
      this.apiUrl = `https://${currentHostname.replace('8080', '8000')}`;
    } else {
      this.apiUrl = 'http://localhost:8000';
    }
    
    // Debug: Log the API URL being used
    console.log('🔗 API URL configured:', this.apiUrl);
    console.log('🌐 Current window location:', window.location.href);
  }

  async request(endpoint, method, data) {
    const url = `${this.apiUrl}${endpoint}`;
    const options = {
      method,
      headers: {
        'Content-Type': 'application/json',
      },
      body: data ? JSON.stringify(data) : undefined,
    };

    // Debug: Log the full request details
    console.log('🚀 Making API request:', {
      url,
      method,
      data,
      headers: options.headers
    });

    const response = await fetch(url, options);
    
    console.log('📥 API response status:', response.status, response.statusText);
    
    if (!response.ok) {
      throw new Error(`API error: ${response.status} ${response.statusText}`);
    }
    
    return response.json();
  }

  async sendMessage(player, message) {
    try {
      console.log('=== API DEBUG ===');
      console.log('Player object:', player);
      console.log('Character ID being sent:', player.id);
      console.log('Character name:', player.name);
      console.log('Message:', message);
      console.log('=================');
      
      const data = await this.request('/chat', 'POST', {
        message,
        character_id: player.id
      });
      
      return data.response;
    } catch (error) {
      console.error('Error sending message to API:', error);
      return this.getFallbackResponse(player);
    }
  }

  getFallbackResponse(player) {
    return `I'm sorry, ${player.name || 'the player'} is unavailable at the moment. Please try again later.`;
  }

  async resetMemory() {
    try {
      const response = await fetch(`${this.apiUrl}/reset-memory`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        }
      });
      
      if (!response.ok) {
        throw new Error('Failed to reset memory');
      }
      
      return await response.json();
    } catch (error) {
      console.error('Error resetting memory:', error);
      throw error;
    }
  }
}

export default new ApiService(); 