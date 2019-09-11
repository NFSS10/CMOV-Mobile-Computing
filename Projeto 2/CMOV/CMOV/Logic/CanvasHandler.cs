using System;
using System.Collections.Generic;
using System.Text;
using CMOV.Models;
using SkiaSharp;
using SkiaSharp.Views.Forms;

namespace CMOV.Logic
{
    public class CanvasHandler
    {
        public static void CanvasDraw(SKPaintSurfaceEventArgs e, StockObject stock1, StockObject stock2, bool extended, bool doubleGraphScale)
        {
            SKCanvas canvas = e.Surface.Canvas;
            int quotes = extended ? 30 : 7;

            int width = e.Info.Width;
            int height = e.Info.Height;
            int marginX = (int)(width * 0.1);
            int marginY = (int)(height * 0.1);

            float sideStep = (float)(width - marginX * 2) / (quotes - 1);
            float maxValue1 = -1;
            float maxValue2 = -1;
            float minValue1 = -1;
            float minValue2 = -1;

            if (!doubleGraphScale)
            {
                maxValue1 = GetMaxValue(stock1, stock2, quotes);
                minValue1 = GetMinValue(stock1, stock2, quotes);
            }
            else
            {
                maxValue1 = GetMaxValue(stock1, null, quotes);
                minValue1 = GetMinValue(stock1, null, quotes);
                maxValue2 = GetMaxValue(null, stock2, quotes);
                minValue2 = GetMinValue(null, stock2, quotes);
            }
            


            //Fill Background
            canvas.Clear(SKColors.WhiteSmoke);


            //Draw Axis
            #region Draw Axis
            SKPaint axisPaint = new SKPaint
            {
                Style = SKPaintStyle.Stroke,
                Color = SKColors.Black,
                StrokeWidth = 5,
            };

            SKPath axisLines = new SKPath();

            axisLines.MoveTo(marginX, marginY);
            axisLines.LineTo(marginX, height - marginY);
            axisLines.LineTo(width - marginX, height - marginY);
            
            if (doubleGraphScale)
            {
                axisLines.LineTo(width - marginX, marginY);
            }

            canvas.DrawPath(axisLines, axisPaint);
            #endregion


            //Draw Labels
            #region Write Labels
            SKPoint maxValueYaxisLeftLabel = new SKPoint
            {
                X = (float)marginX / 4,
                Y = (float)marginY * (float)1.5,
            };
            SKPoint minValueYaxisLeftLabel = new SKPoint
            {
                X = (float)marginX / 4,
                Y = (float)height - marginY
            };
            SKPoint maxValueYaxisRightLabel = new SKPoint
            {
                X = width - (float)marginX / (float)1.1,
                Y = (float)marginY * (float)1.5,
            };
            SKPoint minValueYaxisRightLabel = new SKPoint
            {
                X = width - (float)marginX / (float)1.1,
                Y = (float)height - marginY
            };
            SKPoint startDateXaxisLabel = new SKPoint
            {
                X = marginX * (float)2.3,
                Y = height - marginY / 2,
            };
            SKPoint endDateXaxisLabel = new SKPoint
            {
                X = width - marginX * 4,
                Y = height - marginY / 2,
            };

            string startDateLabel = stock1 != null ? stock1.results[quotes - 1].timestamp.ToString().Split(' ')[0] : "dd/MM/yyyy";
            string maxValueLeftLabel = maxValue1 == 0 ? "max" : ((int)maxValue1).ToString();
            string minValueLeftLabel = minValue1 == int.MaxValue ? "0" : ((int)minValue1).ToString();
            string maxValueRightLabel = "";
            string minValueRightLabel = "";

            if (doubleGraphScale)
            {
                maxValueRightLabel = maxValue2 == 0 ? "max" : ((int)maxValue2).ToString();
                minValueRightLabel = minValue2 == int.MaxValue ? "0" : ((int)minValue2).ToString();
            }

            SKPaint labelPaint = new SKPaint
            {
                Style = SKPaintStyle.Fill,
                Color = SKColors.Black,
                StrokeWidth = 5,
            };
            labelPaint.TextSize = (float)(height / 25);
            canvas.DrawText(maxValueLeftLabel, maxValueYaxisLeftLabel, labelPaint);
            canvas.DrawText(minValueLeftLabel, minValueYaxisLeftLabel, labelPaint);

            string tickerAxis = (stock1 == null) ? "" : "("+stock1.results[0].symbol+")";
            maxValueYaxisLeftLabel.Y -= 2 * labelPaint.TextSize;
            canvas.DrawText("USD "+ tickerAxis, maxValueYaxisLeftLabel, labelPaint);


            if (doubleGraphScale)
            {
                canvas.DrawText(maxValueRightLabel, maxValueYaxisRightLabel, labelPaint);
                canvas.DrawText(minValueRightLabel, minValueYaxisRightLabel, labelPaint);

                tickerAxis = (stock2 == null) ? "" : "("+stock2.results[0].symbol + ")";
                maxValueYaxisRightLabel.Y -= 2*labelPaint.TextSize;
                maxValueYaxisRightLabel.X *= 0.90f;
                canvas.DrawText("USD " + tickerAxis, maxValueYaxisRightLabel, labelPaint);
            }

            canvas.DrawText(startDateLabel, startDateXaxisLabel, labelPaint);
            canvas.DrawText(DateTime.Today.ToString("dd/MM/yyyy"), endDateXaxisLabel, labelPaint);
            #endregion


            //Draw graph1
            DrawGraphs(canvas, quotes, true, stock1, sideStep, width, height, marginX, marginY, minValue1, maxValue1);
            //Draw graph2
            DrawGraphs(canvas, quotes, false, stock2, sideStep, width, height, marginX, marginY, doubleGraphScale ? minValue2 : minValue1, doubleGraphScale ? maxValue2 : maxValue1);
        }




        private static void DrawGraphs(SKCanvas canvas, int quotes, bool isStock1, StockObject stock, float sideStep, int width, int height, int marginX, int marginY, float minValue, float maxValue)
        {
            SKPaint graphPaint;
            SKPaint textPaint;
            SKPath graphLines = new SKPath();

            string ticker = (stock==null) ? " ": stock.results[0].symbol;


            if (isStock1)
            {
                graphPaint = new SKPaint
                {
                    Style = SKPaintStyle.Stroke,
                    Color = SKColors.Red,
                    StrokeWidth = 5,
                };
                textPaint = new SKPaint
                {
                    Style = SKPaintStyle.Stroke,
                    Color = SKColors.Red,
                    StrokeWidth = 1.5f,
                    TextSize = (float)(height / 20)
                };
            }
            else
            {
                graphPaint = new SKPaint
                {
                    Style = SKPaintStyle.Stroke,
                    Color = SKColors.Green,
                    StrokeWidth = 5,
                };
                textPaint = new SKPaint
                {
                    Style = SKPaintStyle.Stroke,
                    Color = SKColors.Green,
                    StrokeWidth = 1.5f,
                    TextSize = (float)(height / 20)
                }; 
            }
            
            if (stock != null)
            {
                float x = width - marginX;
                float y = GetYPos(stock.results[0].close, height, marginY, maxValue, minValue);

                graphLines.MoveTo(x, y);
                canvas.DrawCircle(x, y, 3, graphPaint);

                for (int i = 1; i < quotes; i++)
                {
                    x = width - marginX - sideStep * i;
                    y = GetYPos(stock.results[i].close, height, marginY, maxValue, minValue);
                    graphLines.LineTo(x, y);
                    canvas.DrawCircle(x, y, 3, graphPaint);
                }

                canvas.DrawPath(graphLines, graphPaint);
                DrawTickerLabel(canvas, textPaint, graphPaint, ticker, width, height, isStock1);
            }
        }


        private static void DrawTickerLabel(SKCanvas canvas, SKPaint textPaint, SKPaint graphPaint, string ticker, int canvasWidth, int canvasHeight, bool isStock1)
        {
            //Dividing canvas in 5 columns
            int columnWidth = canvasWidth / 5;
            int columnNr = isStock1 ? 2 : 3;

            int x = columnWidth * columnNr;
            int y = (int)(canvasHeight * 0.05);

            canvas.DrawCircle(x, y, 3, graphPaint);
            canvas.DrawText(ticker, (int)(x*1.02), (int)(y + textPaint.TextSize/2), textPaint);
        }


        private static float GetMaxValue(StockObject stock1, StockObject stock2, int quotes)
        {
            float res = 0;

            if (stock1 != null)
            {
                for (int i = 0; i < quotes; i++)
                {
                    Result r = stock1.results[i];
                    if (r.close > res)
                    {
                        res = (float)r.close;
                    }
                }
            }

            if (stock2 != null)
            {
                for (int i = 0; i < quotes; i++)
                {
                    Result r = stock2.results[i];
                    if (r.close > res)
                    {
                        res = (float)r.close;
                    }
                }
            }

            return res;
        }


        private static float GetMinValue(StockObject stock1, StockObject stock2, int quotes)
        {
            float res = int.MaxValue;

            if (stock1 != null)
            {
                for (int i = 0; i < quotes; i++)
                {
                    Result r = stock1.results[i];
                    if (r.close < res)
                    {
                        res = (float)r.close;
                    }
                }
            }

            if (stock2 != null)
            {
                for (int i = 0; i < quotes; i++)
                {
                    Result r = stock2.results[i];
                    if (r.close < res)
                    {
                        res = (float)r.close;
                    }
                }
            }

            return res;
        }


        private static float GetYPos(double stockClose, int height, int marginY, float maxValue, float minValue)
        {
            float graphHeight = height - marginY * 2;
            float range = maxValue - minValue;

            return graphHeight - (float)(stockClose - minValue) * graphHeight / range + marginY;
        }

    }
}
