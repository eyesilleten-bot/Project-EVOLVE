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





## Bu Proje Ne Yapıyor? — Teknik Bilmeyenler İçin

Project EVOLVE'un temel amacı şu soruyu araştırmaktır:

**Bir bilgisayar programı, her değişikliği insan tarafından yazılmadan, küçük değişiklikler deneyerek zaman içinde daha iyi hale gelebilir mi?**

Bunu basitçe şöyle düşünebilirsiniz:

Bir grup küçük program aynı görevi yapmaya çalışır.

Bazıları görevi daha iyi yapar, bazıları daha kötü yapar.

Daha iyi çalışan programlar korunur.

Sonra onların biraz değiştirilmiş yeni versiyonları oluşturulur.

Bu süreç tekrar tekrar devam eder.

Amaç, zaman içinde sistemin kendi başına işe yarayan yeni program yapıları bulup bulamayacağını gözlemlemektir.

Project EVOLVE'un araştırdığı temel fikir şudur:

**"Programlar da bir tür seçilim ve değişim süreciyle evrimleşebilir mi?"**

Bu proje profesyonel programlama bilgisi olmadan, yapay zekâ destekli bir geliştirme süreciyle oluşturulmuştur.

Projenin fikri, hedefleri, deneylerin yönü ve hangi sonuçların araştırılacağı kullanıcı tarafından belirlenmiş; kodlama, teknik mimari ve uygulama sürecinde yapay zekâ yoğun olarak kullanılmıştır.

V1'in amacı kendi genel amaçlı programlama dilini tamamlamak değildir. Ama sistemin program yapılarını değiştirebildiğini, yeni kod parçaları oluşturabildiğini ve bazı evrimleşmiş yapıların gerçekten faydalı hale gelebildiğini göstermekti.


## İş Görüşmesinde 30 Saniyede Nasıl Anlatırım?

Project EVOLVE, programların zaman içinde kendi yapılarını değiştirerek daha iyi hale gelip gelemeyeceğini araştırdığım deneysel bir projedir.

Basitçe anlatırsam, sistem birçok farklı küçük program oluşturur, bunların aynı görevi ne kadar iyi yaptığını ölçer ve daha başarılı olanların değiştirilmiş yeni versiyonlarını üretir.

Bu süreci tekrar tekrar çalıştırarak, sistemin benim tek tek yazmadığım faydalı program parçaları geliştirip geliştiremeyeceğini test ettim.

Ben profesyonel bir yazılımcı değilim. Projenin fikrini, hedefini, hangi deneylerin yapılacağını ve sonuçların nasıl değerlendirileceğini ben belirledim. Kodlama ve teknik mimari tarafında yapay zekâyı yoğun şekilde kullandım.

V1 sonunda çalışan bir evrim sistemi, evrimleşmiş program yapıları, faydalı olduğu ölçülmüş bazı kod parçaları ve bağımsız çalışabilen bir çıktı formatı elde ettim.

Kısacası bu proje benim için şu sorunun deneyidir:

**"Bir program, insanın her adımı tek tek yazmasına gerek kalmadan, deneme ve seçilim yoluyla kendi yapısını geliştirebilir mi?"**


## İş Görüşmesinde 30 Saniyede Nasıl Anlatırım?

Project EVOLVE, programların zaman içinde kendi yapılarını değiştirerek daha iyi hale gelip gelemeyeceğini araştırdığım deneysel bir projedir.

Basitçe anlatırsam, sistem birçok farklı küçük program oluşturur, bunların aynı görevi ne kadar iyi yaptığını ölçer ve daha başarılı olanların değiştirilmiş yeni versiyonlarını üretir.

Bu süreci tekrar tekrar çalıştırarak, sistemin benim tek tek yazmadığım faydalı program parçaları geliştirip geliştiremeyeceğini test ettim.

Ben profesyonel bir yazılımcı değilim. Projenin fikrini, hedefini, hangi deneylerin yapılacağını ve sonuçların nasıl değerlendirileceğini ben belirledim. Kodlama ve teknik mimari tarafında yapay zekâyı yoğun şekilde kullandım.

V1 sonunda çalışan bir evrim sistemi, evrimleşmiş program yapıları, faydalı olduğu ölçülmüş bazı kod parçaları ve bağımsız çalışabilen bir çıktı formatı elde ettim.

Kısacası bu proje benim için şu sorunun deneyidir:

**"Bir program, insanın her adımı tek tek yazmasına gerek kalmadan, deneme ve seçilim yoluyla kendi yapısını geliştirebilir mi?"**

