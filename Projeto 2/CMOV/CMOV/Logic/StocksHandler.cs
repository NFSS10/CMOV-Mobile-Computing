using System;
using System.Collections.Generic;
using System.Text;
using CMOV.Models;
using Newtonsoft.Json;
using System.Net;
using System.Net.Http;
using System.Threading.Tasks;

namespace CMOV.Logic
{
    //############ If you get to the limit of requests, it throws an exception
    public class StocksHandler
    {
        /**
         *  Extra while testing 
         **/
        //static string apiKey = "ce63bb66bee0c6a3762e9adcebe4bd7d";
        //static string apiKey = "eac5a31263495990a990b9d96a723b9e";
        //static string apiKey = "606c5cc066f96ea450b3419756d216d2";

        static string apiKey = "b8f4ae6c45eae8a3b94fb11bcd221fb7";

        //Get Stock Data synchronously (this method holds the main thread)
        public static StockObject GetStockData(String symbol)
        {
            String startDate = "20180101";
            String endDate = DateTime.Today.ToString("yyyyMMdd");
            String maxRecords = "30";
            String url = "https://" + "marketdata.websol.barchart.com/getHistory.json?" +
                "apikey=" + apiKey + "&" +
                "symbol=" + symbol + "&type=daily&" +
                "startDate=" + startDate + "&" +
                "endDate=" + endDate + "&" +
                "maxRecords=" + maxRecords;


            Uri targetUri = new Uri(url);
            System.Net.HttpWebRequest request = (System.Net.HttpWebRequest)System.Net.HttpWebRequest.Create(targetUri);

            var response = request.GetResponse() as HttpWebResponse;
            StockObject res;

            var encoding = ASCIIEncoding.ASCII;
            using (var reader = new System.IO.StreamReader(response.GetResponseStream(), encoding))
            {
                res = JsonConvert.DeserializeObject<StockObject>(reader.ReadToEnd());
            }

            res.results.Reverse();

            return res;
        }




        //Get Stock Data asynchronously
        public async static Task<StockObject> GetStockDataAsync(String symbol)
        {
            String startDate = "20180101";
            String endDate = DateTime.Today.ToString("yyyyMMdd");
            String maxRecords = "30";
            String url = "https://" + "marketdata.websol.barchart.com/getHistory.json?" +
                "apikey=" + apiKey + "&" +
                "symbol=" + symbol + "&type=daily&" +
                "startDate=" + startDate + "&" +
                "endDate=" + endDate + "&" +
                "maxRecords=" + maxRecords;


            using (HttpClient client = new HttpClient())
            { 
                try
                {
                    HttpResponseMessage message = await client.GetAsync(url);
                    if (message.StatusCode == HttpStatusCode.OK)
                    {
                        StockObject res;
                        res = JsonConvert.DeserializeObject<StockObject>(await message.Content.ReadAsStringAsync());
                        res.results.Reverse();
                        return res;
                    }
                    return null;
                }
                catch (Exception e)
                {
                    return null;
                }
            }
        }


    }
}
