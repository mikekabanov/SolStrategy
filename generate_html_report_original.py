"""
Generate professional HTML report for original backtest (3% TP, 120 min timeout)
"""

import pandas as pd
import numpy as np
from datetime import datetime

# Load data
print("Generating HTML report from: data/backtest_trades.csv")
trades_df = pd.read_csv('data/backtest_trades.csv')
signals_df = pd.read_csv('data/signals_pct_3.0_min_120.csv')

# Calculate metrics
total_trades = len(trades_df)
winning_trades = len(trades_df[trades_df['roi'] > 0])
losing_trades = len(trades_df[trades_df['roi'] <= 0])
win_rate_pct = (winning_trades / total_trades * 100) if total_trades > 0 else 0

initial_capital = 10000
position_size = 1000
cum_pnl = np.cumsum(trades_df['pnl'].values)
final_capital = initial_capital + cum_pnl[-1]
total_pnl = cum_pnl[-1]
total_return_pct = (total_pnl / initial_capital * 100)

# Risk metrics
roi_values = trades_df['roi'].values
avg_roi_pct = roi_values.mean() * 100
max_drawdown = (1 - (trades_df['max_loss'] + 1).min()) * 100
profit_factor = abs((trades_df[trades_df['roi'] > 0]['pnl'].sum()) / (trades_df[trades_df['roi'] <= 0]['pnl'].sum() + 1e-6))
sharpe_ratio = np.sqrt(252) * (roi_values.mean() / (roi_values.std() + 1e-6))

# Average metrics
avg_win_pct = trades_df[trades_df['roi'] > 0]['roi'].mean() * 100 if winning_trades > 0 else 0
avg_loss_pct = trades_df[trades_df['roi'] <= 0]['roi'].mean() * 100 if losing_trades > 0 else 0

# Drawdown
running_max = np.maximum.accumulate(initial_capital + cum_pnl)
drawdown_curve = ((initial_capital + cum_pnl) - running_max) / running_max * 100
current_drawdown = drawdown_curve[-1]

# Sample trades
sample_trades = trades_df.head(10).copy()
sample_trades['entry_price'] = sample_trades['entry_price'].astype(float).apply(lambda x: f'${x:.2f}')
sample_trades['exit_price'] = sample_trades['exit_price'].astype(float).apply(lambda x: f'${x:.2f}')
sample_trades['roi'] = (sample_trades['roi'].astype(float) * 100).apply(lambda x: f'{x:.2f}%')
sample_trades['pnl'] = sample_trades['pnl'].astype(float).apply(lambda x: f'${x:.2f}')

# HTML content
html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SOL-USDT Backtest Report | 3% TP + 120 Min Timeout</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #333;
            padding: 20px;
            line-height: 1.6;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 10px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.3);
            overflow: hidden;
        }}
        
        .header {{
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }}
        
        .header h1 {{
            font-size: 28px;
            margin-bottom: 10px;
        }}
        
        .header p {{
            font-size: 14px;
            opacity: 0.9;
        }}
        
        .content {{
            padding: 30px;
        }}
        
        .cards-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        
        .card {{
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            padding: 20px;
            border-radius: 8px;
            border-left: 5px solid #667eea;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            transition: transform 0.2s;
        }}
        
        .card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 5px 20px rgba(0,0,0,0.15);
        }}
        
        .card h3 {{
            color: #667eea;
            font-size: 12px;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 10px;
        }}
        
        .card .value {{
            font-size: 24px;
            font-weight: bold;
            color: #333;
        }}
        
        .card .subtext {{
            font-size: 12px;
            color: #666;
            margin-top: 5px;
        }}
        
        .table-section {{
            margin-bottom: 30px;
        }}
        
        .section-title {{
            font-size: 18px;
            font-weight: bold;
            color: #1e3c72;
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 2px solid #667eea;
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
            background: white;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            border-radius: 5px;
            overflow: hidden;
        }}
        
        th {{
            background: #667eea;
            color: white;
            padding: 12px;
            text-align: left;
            font-weight: 600;
        }}
        
        td {{
            padding: 10px 12px;
            border-bottom: 1px solid #eee;
        }}
        
        tr:hover {{
            background: #f5f5f5;
        }}
        
        tr:last-child td {{
            border-bottom: none;
        }}
        
        .positive {{
            color: #06a77d;
            font-weight: bold;
        }}
        
        .negative {{
            color: #d62828;
            font-weight: bold;
        }}
        
        .neutral {{
            color: #666;
        }}
        
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-bottom: 20px;
        }}
        
        .stat-item {{
            background: #f9f9f9;
            padding: 15px;
            border-radius: 5px;
            border-left: 3px solid #667eea;
        }}
        
        .stat-label {{
            font-size: 12px;
            color: #666;
            text-transform: uppercase;
        }}
        
        .stat-value {{
            font-size: 18px;
            font-weight: bold;
            color: #333;
            margin-top: 5px;
        }}
        
        .visualization {{
            margin: 30px 0;
            text-align: center;
        }}
        
        .visualization img {{
            max-width: 100%;
            height: auto;
            border-radius: 8px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.2);
        }}
        
        .navigation {{
            display: flex;
            justify-content: center;
            gap: 10px;
            margin-top: 30px;
            padding-top: 20px;
            border-top: 2px solid #eee;
        }}
        
        .nav-button {{
            display: inline-block;
            padding: 10px 20px;
            background: #667eea;
            color: white;
            text-decoration: none;
            border-radius: 5px;
            transition: background 0.2s;
            font-size: 14px;
        }}
        
        .nav-button:hover {{
            background: #5568d3;
        }}
        
        .footer {{
            background: #f5f5f5;
            padding: 20px;
            text-align: center;
            color: #666;
            font-size: 12px;
            border-top: 1px solid #ddd;
        }}
        
        .comparison {{
            background: #fffacd;
            border-left: 4px solid #ffd700;
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 20px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎯 SOL-USDT Trading Strategy Backtest</h1>
            <p>Original Strategy: 3% Take Profit | 120-Minute Timeout | $10,000 Starting Capital</p>
        </div>
        
        <div class="content">
            <!-- Key Metrics Cards -->
            <div class="cards-grid">
                <div class="card">
                    <h3>📊 Total Trades</h3>
                    <div class="value">{total_trades}</div>
                    <div class="subtext">{winning_trades} winning, {losing_trades} losing</div>
                </div>
                
                <div class="card">
                    <h3>📈 Win Rate</h3>
                    <div class="value positive">{win_rate_pct:.1f}%</div>
                    <div class="subtext">{winning_trades}/{total_trades} trades profitable</div>
                </div>
                
                <div class="card">
                    <h3>💰 Total Return</h3>
                    <div class="value positive">{total_return_pct:.2f}%</div>
                    <div class="subtext">${total_pnl:,.0f} profit on ${initial_capital:,.0f}</div>
                </div>
                
                <div class="card">
                    <h3>📊 Avg ROI/Trade</h3>
                    <div class="value positive">{avg_roi_pct:.2f}%</div>
                    <div class="subtext">Average return per trade</div>
                </div>
            </div>
            
            <!-- Capital Analysis -->
            <div class="table-section">
                <h2 class="section-title">Capital Flow</h2>
                <div class="stats-grid">
                    <div class="stat-item">
                        <div class="stat-label">Initial Capital</div>
                        <div class="stat-value">${initial_capital:,.0f}</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-label">Final Capital</div>
                        <div class="stat-value positive">${final_capital:,.0f}</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-label">Total P&L</div>
                        <div class="stat-value positive">${total_pnl:,.0f}</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-label">Avg Win</div>
                        <div class="stat-value positive">{avg_win_pct:.2f}%</div>
                    </div>
                </div>
            </div>
            
            <!-- Risk Analysis -->
            <div class="table-section">
                <h2 class="section-title">Risk Metrics</h2>
                <div class="stats-grid">
                    <div class="stat-item">
                        <div class="stat-label">Max Drawdown</div>
                        <div class="stat-value negative">{max_drawdown:.2f}%</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-label">Profit Factor</div>
                        <div class="stat-value">{profit_factor:.2f}x</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-label">Sharpe Ratio</div>
                        <div class="stat-value">{sharpe_ratio:.2f}</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-label">Avg Loss</div>
                        <div class="stat-value negative">{avg_loss_pct:.2f}%</div>
                    </div>
                </div>
            </div>
            
            <!-- Visualization -->
            <div class="visualization">
                <h2 class="section-title">📊 Backtest Visualization</h2>
                <img src="./backtest_results_3pct_120min.png" alt="Backtest Results Visualization">
            </div>
            
            <!-- Sample Trades Table -->
            <div class="table-section">
                <h2 class="section-title">Sample Trades (First 10)</h2>
                <table>
                    <thead>
                        <tr>
                            <th>Trade #</th>
                            <th>Entry Price</th>
                            <th>Exit Price</th>
                            <th>ROI</th>
                            <th>P&L</th>
                            <th>Status</th>
                        </tr>
                    </thead>
                    <tbody>
"""

# Add sample trades
for idx, row in sample_trades.iterrows():
    html_content += f"""                        <tr>
                            <td>{idx + 1}</td>
                            <td>{row['entry_price']}</td>
                            <td>{row['exit_price']}</td>
                            <td class="positive">{row['roi']}</td>
                            <td class="positive">{row['pnl']}</td>
                            <td>{row['status']}</td>
                        </tr>
"""

html_content += """                    </tbody>
                </table>
            </div>
            
            <!-- Strategy Summary -->
            <div class="comparison">
                <h3>🎯 Strategy Parameters</h3>
                <p><strong>Take Profit:</strong> 3% target on entry price</p>
                <p><strong>Time Timeout:</strong> Exit after 120 minutes regardless of profit</p>
                <p><strong>Stop Loss:</strong> 2% maximum loss per trade</p>
                <p><strong>Position Size:</strong> $1,000 USD per trade</p>
                <p><strong>Max Concurrent:</strong> 10 simultaneous positions</p>
                <p><strong>Backtest Period:</strong> ~27 days of minute candles (39,698 bars)</p>
            </div>
            
            <!-- Navigation -->
            <div class="navigation">
                <a href="./index.html" class="nav-button">🏠 Home</a>
                <a href="./report_english.html" class="nav-button">📖 Full Report (EN)</a>
                <a href="./report_russian.html" class="nav-button">📖 Full Report (RU)</a>
                <a href="./report_4pct_2pstop.html" class="nav-button">📊 4% TP Scenario</a>
            </div>
        </div>
        
        <div class="footer">
            <p>Backtest Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p>Strategy: SOL-USDT Machine Learning Trading | Data Source: Moralis on-chain data</p>
            <p><strong>Disclaimer:</strong> Past performance does not guarantee future results. Trading involves substantial risk.</p>
        </div>
    </div>
</body>
</html>"""

# Write HTML
output_html = 'report_3pct_120min.html'
with open(output_html, 'w', encoding='utf-8') as f:
    f.write(html_content)

print(f"✅ HTML report saved to: {output_html}")
