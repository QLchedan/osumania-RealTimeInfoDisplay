using OsuMemoryDataProvider.OsuMemoryModels;
using OsuMemoryDataProvider;
using OsuMemoryDataProvider.OsuMemoryModels.Direct;
using Newtonsoft.Json;
using System;
using System.Text;
using Microsoft.Extensions.ObjectPool;

var builder = WebApplication.CreateBuilder(args);
var app = builder.Build();
#pragma warning disable CS0618
//IOsuMemoryReader _reader = OsuMemoryReader.Instance.GetInstanceForWindowTitleHint(null);
StructuredOsuMemoryReader _sreader = StructuredOsuMemoryReader.Instance.GetInstanceForWindowTitleHint(null);

T ReadProperty<T>(object readObj, string propName, T defaultValue = default) where T : struct
{
    if (_sreader.TryReadProperty(readObj, propName, out var readResult))
        return (T)readResult;

    return defaultValue;
}

T ReadClassProperty<T>(object readObj, string propName, T defaultValue = default) where T : class
{
    if (_sreader.TryReadProperty(readObj, propName, out var readResult))
        return (T)readResult;

    return defaultValue;
}
int ReadInt(object readObj, string propName)
    => ReadProperty<int>(readObj, propName, -5);
short ReadShort(object readObj, string propName)
    => (short)ReadProperty<ushort>(readObj, propName, 5);

float ReadFloat(object readObj, string propName)
    => ReadProperty<float>(readObj, propName, -5f);

string ReadString(object readObj, string propName)
    => ReadClassProperty<string>(readObj, propName, "INVALID READ");
app.MapGet("/getjson", async () =>
{
    OsuBaseAddresses baseAddresses = new OsuBaseAddresses();
    _sreader.TryRead(baseAddresses.Beatmap);
    _sreader.TryRead(baseAddresses.Skin);
    _sreader.TryRead(baseAddresses.GeneralData);
    _sreader.TryRead(baseAddresses.BanchoUser);
    if (baseAddresses.GeneralData.OsuStatus == OsuMemoryStatus.Playing)
        _sreader.TryRead(baseAddresses.Player);
    return JsonConvert.SerializeObject(baseAddresses, Formatting.Indented);
});

app.Run("http://localhost:9810");