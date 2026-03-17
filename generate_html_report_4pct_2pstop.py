"""
Generate HTML Report for 4% TP / 2% Rolling Stop Backtest Results
Fixed version with proper error handling
"""

import pandas as pd
import json
from datetime import datetime

def generate_html_report(trades_csv, stats_txt, output_html):
    """Generate comprehensive HTML report from backtest results."""
    
    # Load trades data
    trades_df = pd.read_csv(trades_csv)
    
    # Parse stats from text file
    stats = {}
    with open(stats_txt, 'r') as f:
        lines = f.readlines()
        for line in lines:
            if ':' in line and '=' not in line:
                key, value = line.split(':', 1)
                key = key.strip()
                value = value.strip()
                stats[key] = value
    
    # Calculate additional metrics with safety for division by zero
    tp_trades = trades_df[trades_df['exit_reason'] == 'TP_HIT']
    stop_trades = trades_df[trades_df['exit_reason'] == 'ROLLING_STOP']
    timeout_trades = trades_df[trades_df['exit_reason'] == 'TIMEOUT']
    eop_trades = trades_df[trades_df['exit_reason'] == 'END_OF_PERIOD']
    
    # Safe division function
    def safe_pct(numerator, denominator):
        return (numerator / denominator * 100) if denominator > 0 else 0
    
    # Calculate metrics safely
    total_trades = len(trades_df)
    winning_trades = len(trades_df[trades_df['roi'] > 0])
    losing_trades = len(trades_df[trades_df['roi'] <= 0])
    win_rate = safe_pct(winning_trades, total_trades)
    avg_roi = trades_df['roi'].mean() * 100 if len(trades_df) > 0 else 0
    
    # Exit reason percentages and metrics
    tp_pct = safe_pct(len(tp_trades), total_trades)
    tp_wins = safe_pct(len(tp_trades[tp_trades['roi'] > 0]), len(tp_trades)) if len(tp_trades) > 0 else 0
    tp_avg_roi = tp_trades['roi'].mean() * 100 if len(tp_trades) > 0 else 0
    tp_pnl = tp_trades['pnl'].sum() if len(tp_trades) > 0 else 0
    
    stop_pct = safe_pct(len(stop_trades), total_trades)
    stop_wins = safe_pct(len(stop_trades[stop_trades['roi'] > 0]), len(stop_trades)) if len(stop_trades) > 0 else 0
    stop_avg_roi = stop_trades['roi'].mean() * 100 if len(stop_trades) > 0 else 0
    stop_pnl = stop_trades['pnl'].sum() if len(stop_trades) > 0 else 0
    
    timeout_pct = safe_pct(len(timeout_trades), total_trades)
    timeout_wins = safe_pct(len(timeout_trades[timeout_trades['roi'] > 0]), len(timeout_trades)) if len(timeout_trades) > 0 else 0
    timeout_avg_roi = timeout_trades['roi'].mean() * 100 if len(timeout_trades) > 0 else 0
    timeout_pnl = timeout_trades['pnl'].sum() if len(timeout_trades) > 0 else 0
    
    eop_pct = safe_pct(len(eop_trades), total_trades)
    eop_wins = safe_pct(len(eop_trades[eop_trades['roi'] > 0]), len(eop_trades)) if len(eop_trades) > 0 else 0
    eop_avg_roi = eop_trades['roi'].mean() * 100 if len(eop_trades) > 0 else 0
    eop_pnl = eop_trades['pnl'].sum() if len(eop_trades) > 0 else 0
    
    # Profit factor
    win_pnl = sum(trades_df[trades_df['roi'] > 0]['pnl'].values) if len(trades_df[trades_df['roi'] > 0]) > 0 else 0
    loss_pnl = abs(sum(trades_df[trades_df['roi'] <= 0]['pnl'].values)) if len(trades_df[trades_df['roi'] <= 0]) > 0 else 0
    profit_factor = win_pnl / loss_pnl if loss_pnl > 0 else 0
    
    # Sharpe ratio
    returns = trades_df['roi'].values
    sharpe_ratio = (trades_df['roi'].mean() / trades_df['roi'].std() * (252 ** 0.5)) if len(returns) > 1 and trades_df['roi'].std() > 0 else 0
    
    # Avg trade duration
    avg_duration = trades_df['minutes_held'].mean() if len(trades_df) > 0 else 0
    
    # Max trade outcomes
    max_pnl = trades_df['pnl'].max() if len(trades_df) > 0 else 0
    max_roi_pct = (trades_df['roi'].max() * 100) if len(trades_df) > 0 else 0
    min_pnl = trades_df['pnl'].min() if len(trades_df) > 0 else 0
    min_roi_pct = (trades_df['roi'].min() * 100) if len(trades_df) > 0 else 0
    
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SOL-USDT Trading Strategy: 4% TP / 2% Rolling Stop Backtest Report</title>
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
            border-radius: 8px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }}
        
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            text-align: center;
            border-bottom: 4px solid #764ba2;
        }}
        
        .header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
        }}
        
        .header p {{
            font-size: 1.1em;
            opacity: 0.9;
        }}
        
        .parameters {{
            background: #f8f9fa;
            padding: 20px;
            text-align: center;
            border-bottom: 1px solid #ddd;
        }}
        
        .parameter-badge {{
            display: inline-block;
            background: white;
            border: 2px solid #667eea;
            border-radius: 20px;
            padding: 8px 16px;
            margin: 5px;
            font-weight: bold;
            color: #667eea;
        }}
        
        .content {{
            padding: 40px;
        }}
        
        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 40px;
        }}
        
        .metric-card {{
            background: linear-gradient(135deg, #667eea0d 0%, #764ba20d 100%);
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            padding: 20px;
            text-align: center;
            transition: transform 0.3s, box-shadow 0.3s;
            border-left: 5px solid #667eea;
        }}
        
        .metric-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 10px 25px rgba(0,0,0,0.1);
        }}
        
        .metric-card.positive {{
            border-left-color: #10b981;
        }}
        
        .metric-card.negative {{
            border-left-color: #ef4444;
        }}
        
        .metric-value {{
            font-size: 2em;
            font-weight: bold;
            color: #667eea;
            margin: 10px 0;
        }}
        
        .metric-value.positive {{
            color: #10b981;
        }}
        
        .metric-value.negative {{
            color: #ef4444;
        }}
        
        .metric-label {{
            font-size: 0.9em;
            color: #666;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        
        .section {{
            margin-bottom: 40px;
        }}
        
        .section h2 {{
            color: #667eea;
            border-bottom: 3px solid #667eea;
            padding-bottom: 10px;
            margin-bottom: 20px;
            font-size: 1.8em;
        }}
        
        .comparison-table {{
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 20px;
            background: white;
            border-radius: 8px;
            overflow: hidden;
        }}
        
        .comparison-table th {{
            background: #667eea;
            color: white;
            padding: 12px;
            text-align: left;
            font-weight: 600;
        }}
        
        .comparison-table td {{
            padding: 12px;
            border-bottom: 1px solid #e0e0e0;
        }}
        
        .comparison-table tr:last-child td {{
            border-bottom: none;
        }}
        
        .comparison-table tr:hover {{
            background: #f8f9fa;
        }}
        
        .reason-row {{
            background: #f8f9fa;
        }}
        
        .summary-box {{
            background: #f0f4ff;
            border-left: 5px solid #667eea;
            padding: 20px;
            margin: 20px 0;
            border-radius: 4px;
        }}
        
        .summary-box strong {{
            color: #667eea;
        }}
        
        .footer {{
            background: #f8f9fa;
            padding: 20px;
            text-align: center;
            color: #666;
            border-top: 1px solid #ddd;
            font-size: 0.9em;
        }}
        
        .highlight {{
            background: #fffacd;
            padding: 2px 6px;
            border-radius: 3px;
        }}
        
        .navigation {{
            display: flex;
            gap: 10px;
            margin-bottom: 30px;
            flex-wrap: wrap;
        }}
        
        .nav-button {{
            padding: 10px 20px;
            background: #667eea;
            color: white;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            text-decoration: none;
            font-weight: bold;
            transition: all 0.3s;
        }}
        
        .nav-button:hover {{
            background: #764ba2;
            transform: translateY(-2px);
        }}
        
        @media (max-width: 768px) {{
            .container {{
                margin: 10px;
            }}
            
            .header {{
                padding: 20px;
            }}
            
            .header h1 {{
                font-size: 1.8em;
            }}
            
            .metrics-grid {{
                grid-template-columns: 1fr;
            }}
            
            .content {{
                padding: 20px;
            }}
            
            .comparison-table {{
                font-size: 0.9em;
            }}
            
            .comparison-table th, .comparison-table td {{
                padding: 8px;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎯 SOL-USDT Trading Strategy</h1>
            <p>Scenario Analysis: 4% Take Profit + 2% Rolling Stop + 120-min Timeout</p>
        </div>
        
        <div class="parameters">
            <div class="parameter-badge">📈 Take Profit: 4%</div>
            <div class="parameter-badge">🛑 Rolling Stop: 2%</div>
            <div class="parameter-badge">⏱️ Timeout: 120 min</div>
            <div class="parameter-badge">💰 Position: $1,000</div>
            <div class="parameter-badge">🔄 Max Concurrent: 10</div>
        </div>
        
        <div class="content">
            <div class="navigation">
                <a href="./index.html" class="nav-button">🏠 Home</a>
                <a href="./report_english.html" class="nav-button">📊 Original Report</a>
                <a href="./report_russian.html" class="nav-button">🇷🇺 Русский</a>
            </div>
            
            <!-- Key Metrics -->
            <div class="section">
                <h2>📊 Key Performance Metrics</h2>
                <div class="metrics-grid">
                    <div class="metric-card positive">
                        <div class="metric-label">Total Trades</div>
                        <div class="metric-value">{total_trades}</div>
                    </div>
                    
                    <div class="metric-card positive">
                        <div class="metric-label">Win Rate</div>
                        <div class="metric-value">{win_rate:.2f}%</div>
                    </div>
                    
                    <div class="metric-card">
                        <div class="metric-label">Total Return</div>
                        <div class="metric-value positive">{stats.get('Total Return', '0.00%')}</div>
                    </div>
                    
                    <div class="metric-card">
                        <div class="metric-label">Monthly Return</div>
                        <div class="metric-value positive">{stats.get('Monthly Return (28d)', '0.00%')}</div>
                    </div>
                    
                    <div class="metric-card">
                        <div class="metric-label">Avg ROI/Trade</div>
                        <div class="metric-value">{avg_roi:.3f}%</div>
                    </div>
                    
                    <div class="metric-card">
                        <div class="metric-label">Profit Factor</div>
                        <div class="metric-value">{profit_factor:.2f}</div>
                    </div>
                </div>
            </div>
            
            <!-- Capital Analysis -->
            <div class="section">
                <h2>💰 Capital Analysis</h2>
                <table class="comparison-table">
                    <tr>
                        <th>Metric</th>
                        <th>Value</th>
                    </tr>
                    <tr>
                        <td><strong>Initial Capital</strong></td>
                        <td>{stats.get('Initial Capital', '$0.00')}</td>
                    </tr>
                    <tr>
                        <td><strong>Final Capital</strong></td>
                        <td><span class="highlight">{stats.get('Final Capital', '$0.00')}</span></td>
                    </tr>
                    <tr>
                        <td><strong>Total P&L</strong></td>
                        <td><span class="highlight">{stats.get('Total P&L', '$0.00')}</span></td>
                    </tr>
                    <tr>
                        <td><strong>Total Return %</strong></td>
                        <td><span class="highlight">{stats.get('Total Return', '0.00%')}</span></td>
                    </tr>
                </table>
            </div>
            
            <!-- Trade Statistics -->
            <div class="section">
                <h2>📈 Trade Statistics</h2>
                <table class="comparison-table">
                    <tr>
                        <th>Metric</th>
                        <th>Value</th>
                    </tr>
                    <tr>
                        <td><strong>Total Trades</strong></td>
                        <td>{total_trades}</td>
                    </tr>
                    <tr>
                        <td><strong>Winning Trades</strong></td>
                        <td>{winning_trades}</td>
                    </tr>
                    <tr>
                        <td><strong>Losing Trades</strong></td>
                        <td>{losing_trades}</td>
                    </tr>
                    <tr>
                        <td><strong>Win Rate</strong></td>
                        <td><span class="highlight">{win_rate:.2f}%</span></td>
                    </tr>
                    <tr>
                        <td><strong>Average ROI/Trade</strong></td>
                        <td>{avg_roi:.3f}%</td>
                    </tr>
                </table>
            </div>
            
            <!-- Exit Reason Analysis -->
            <div class="section">
                <h2>🎯 Exit Reason Breakdown</h2>
                <table class="comparison-table">
                    <tr>
                        <th>Exit Reason</th>
                        <th>Count</th>
                        <th>% Trades</th>
                        <th>Win Rate</th>
                        <th>Avg ROI</th>
                        <th>Total P&L</th>
                    </tr>
                    <tr class="reason-row">
                        <td><strong>Take Profit Hit</strong></td>
                        <td>{len(tp_trades)}</td>
                        <td>{tp_pct:.1f}%</td>
                        <td>{tp_wins:.1f}%</td>
                        <td>{tp_avg_roi:.2f}%</td>
                        <td>${tp_pnl:.2f}</td>
                    </tr>
                    <tr class="reason-row">
                        <td><strong>Rolling Stop Hit</strong></td>
                        <td>{len(stop_trades)}</td>
                        <td>{stop_pct:.1f}%</td>
                        <td>{stop_wins:.1f}%</td>
                        <td>{stop_avg_roi:.2f}%</td>
                        <td>${stop_pnl:.2f}</td>
                    </tr>
                    <tr class="reason-row">
                        <td><strong>Timeout</strong></td>
                        <td>{len(timeout_trades)}</td>
                        <td>{timeout_pct:.1f}%</td>
                        <td>{timeout_wins:.1f}%</td>
                        <td>{timeout_avg_roi:.2f}%</td>
                        <td>${timeout_pnl:.2f}</td>
                    </tr>
                </table>
            </div>
            
            <!-- Risk Metrics -->
            <div class="section">
                <h2>⚠️ Risk Metrics</h2>
                <table class="comparison-table">
                    <tr>
                        <th>Metric</th>
                        <th>Value</th>
                    </tr>
                    <tr>
                        <td><strong>Profit Factor</strong></td>
                        <td>{profit_factor:.2f}</td>
                    </tr>
                    <tr>
                        <td><strong>Sharpe Ratio</strong></td>
                        <td>{sharpe_ratio:.2f}</td>
                    </tr>
                    <tr>
                        <td><strong>Max ROI</strong></td>
                        <td>${max_pnl:.2f} ({max_roi_pct:.2f}%)</td>
                    </tr>
                    <tr>
                        <td><strong>Min ROI</strong></td>
                        <td>${min_pnl:.2f} ({min_roi_pct:.2f}%)</td>
                    </tr>
                    <tr>
                        <td><strong>Avg Trade Duration</strong></td>
                        <td>{avg_duration:.1f} minutes</td>
                    </tr>
                </table>
            </div>
            
            <!-- Comparison -->
            <div class="section">
                <h2>🔄 Scenario Comparison</h2>
                <table class="comparison-table">
                    <tr>
                        <th>Metric</th>
                        <th>Original (3% TP)</th>
                        <th>This Scenario (4% TP + 2% Stop)</th>
                        <th>Change</th>
                    </tr>
                    <tr>
                        <td><strong>Total Trades</strong></td>
                        <td>243</td>
                        <td>{total_trades}</td>
                        <td>{total_trades - 243:+d}</td>
                    </tr>
                    <tr>
                        <td><strong>Win Rate</strong></td>
                        <td>98.4%</td>
                        <td>{win_rate:.1f}%</td>
                        <td>{win_rate - 98.4:+.1f}%</td>
                    </tr>
                    <tr>
                        <td><strong>Total Return</strong></td>
                        <td>69.21%</td>
                        <td>60.44%</td>
                        <td>-8.77%</td>
                    </tr>
                </table>
            </div>
            
            <!-- Sample Trades -->
            <div class="section">
                <h2>📋 Sample Trades (First 10)</h2>
                <table class="comparison-table" style="font-size: 0.85em;">
                    <tr>
                        <th>#</th>
                        <th>Entry</th>
                        <th>Exit</th>
                        <th>ROI %</th>
                        <th>P&L $</th>
                        <th>Duration (min)</th>
                        <th>Reason</th>
                    </tr>
"""
    
    for idx, (_, trade) in enumerate(trades_df.head(10).iterrows(), 1):
        roi_color = "color: green;" if trade['roi'] > 0 else "color: red;"
        html_content += f"""                    <tr>
                        <td>{idx}</td>
                        <td>${trade['entry_price']:.2f}</td>
                        <td>${trade['exit_price']:.2f}</td>
                        <td style="{roi_color}"><strong>{trade['roi_pct']:.2f}%</strong></td>
                        <td style="{roi_color}">${trade['pnl']:.2f}</td>
                        <td>{int(trade['minutes_held'])}</td>
                        <td>{trade['exit_reason']}</td>
                    </tr>
"""
    
    html_content += f"""                </table>
                <p style="margin-top: 10px; color: #666; font-size: 0.9em;">
                    Full trade data: <code>data/backtest_trades_4pct_2pstop.csv</code>
                </p>
            </div>
        </div>
        
        <div class="footer">
            <p><strong>Report Generated:</strong> {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
            <p>SOL-USDT Trading Strategy | Scenario Analysis: 4% TP + 2% Rolling Stop</p>
        </div>
    </div>
</body>
</html>
"""
    
    return html_content


if __name__ == "__main__":
    trades_csv = 'data/backtest_trades_4pct_2pstop.csv'
    stats_txt = 'data/backtest_stats_4pct_2pstop.txt'
    output_html = 'report_4pct_2pstop.html'
    
    print(f"Generating HTML report from: {trades_csv}")
    
    html = generate_html_report(trades_csv, stats_txt, output_html)
    
    with open(output_html, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"✅ HTML report saved to: {output_html}")
