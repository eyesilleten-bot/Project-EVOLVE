# Project EVOLVE

[English README](README.md)

Project EVOLVE, yalnızca sabit sayısal parametreleri optimize etmek yerine çalıştırılabilir program yapılarını evrimleştirmeye odaklanan deneysel bir evrimsel programlama sistemidir.

## V1 Durumu

Version 1.0, araştırma sistemini kararlı bir deneysel kilometre taşında dondurur.

Project EVOLVE V1 şu anda şunları destekler:

- population tabanlı program evrimi
- AST tabanlı çalıştırılabilir genomlar
- program yapısının mutasyonu ve seçilimi
- evrimleşmiş opcode'lar
- evrimleşmiş function'lar
- program architecture evrimi
- lineage ve diversity takibi
- üretilmiş Python kodunun çalıştırılması
- dual execution validation
- EVIR standalone runtime

Proje, fitness üzerinde ölçülebilir causal katkısı bulunan evrimleşmiş instruction'lar üretildiğini deneysel olarak göstermiştir.

## V1 Ne Değildir?

V1, tamamen kendi kendine ortaya çıkmış genel amaçlı bir programlama dili oluşturduğunu iddia etmez.

Faydalı evrimleşmiş function'lar ve tam language autonomy gelecek sürümlerin araştırma hedefleri olarak kalmaktadır.

## Hızlı Başlangıç

Demo:

    python evolve.py demo

Release testi:

    python evolve.py test

## Mimari

Temel bileşenler:

- EvolutionEngine
- Genome
- ASTProgram
- ProgramArchitecture
- EvolvedLanguage
- Evaluator
- DualExecutionValidator
- EVIR standalone runtime

## Araştırma Yönü

Gelecekte araştırılabilecek konular:

- kalıcı ve faydalı evrimleşmiş function'lar
- legacy bağımsız programlar
- yeniden kullanılabilir evrimleşmiş vocabulary
- otonom evrimleşmiş dil yapıları
- harici program üretimi

## V1 Yaklaşımı

V1 bilinçli olarak küçük, tekrar üretilebilir ve kararlı bir araştırma sürümü olarak dondurulmuştur.

Amaç, açık uçlu dil evrimi araştırmasını beklerken yayını süresiz ertelemek yerine çalışan bir evrimsel programlama sistemini koruyup yayınlamaktır.

## Lisans

MIT License altında yayınlanmaktadır. Ayrıntılar için `LICENSE` dosyasına bakın.




