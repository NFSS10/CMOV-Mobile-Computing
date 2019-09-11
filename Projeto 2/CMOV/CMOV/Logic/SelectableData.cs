using System;
using System.Collections.Generic;
using System.Text;

namespace CMOV.Logic
{
    public class SelectableData<T>
    {
        public T data { get; set; }
        public bool isSelected { get; set; }

        public SelectableData(T data)
        {
            this.data = data;
            this.isSelected = false;
        }
    }


}
