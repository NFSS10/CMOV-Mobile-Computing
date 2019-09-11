using System;
using System.Collections.Generic;
using System.Text;

namespace CMOV.Models
{

    public class Status
    {
        public int code { get; set; }
        public string message { get; set; }
    }

    public class Result
    {
        public string symbol { get; set; }
        public DateTime timestamp { get; set; }
        public string tradingDay { get; set; }
        public double open { get; set; }
        public double high { get; set; }
        public double low { get; set; }
        public double close { get; set; }
        public int volume { get; set; }
        public object openInterest { get; set; }
    }

    public class StockObject
    {
        public Status status { get; set; }
        public List<Result> results { get; set; }
    }
}
