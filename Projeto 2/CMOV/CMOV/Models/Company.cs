using System;
using System.Collections.Generic;
using System.Text;

namespace CMOV.Logic
{
    class Company
    {
        public string name { get; set; }
        public string ticker { get; set; }
        public string imgUrl { get; set; }


        public Company(string name, string ticker, string imgUrl)
        {
            this.name = name;
            this.ticker = ticker;
            this.imgUrl = imgUrl;
        }

    }
}
