# Literatür Taraması ve İlgili Çalışmalar

## 1. Giriş

Parola tabanlı kimlik doğrulama, modern bilgi sistemlerinde hâlâ en yaygın kullanılan güvenlik mekanizmalarından biridir. Çok faktörlü kimlik doğrulama, biyometrik doğrulama ve donanımsal güvenlik anahtarları gibi alternatifler yaygınlaşmış olsa da, parola sistemleri hem düşük maliyetli olmaları hem de kullanıcılar tarafından kolay benimsenmeleri nedeniyle web uygulamalarında, mobil sistemlerde ve kurumsal servislerde önemini korumaktadır. Bununla birlikte, kullanıcıların hatırlanabilir parola seçme eğilimi, parolaların tahmin edilebilir örüntüler içermesine yol açmaktadır. Bu nedenle parola güvenliği yalnızca karakter uzunluğu veya karakter çeşitliliği ile değil, aynı zamanda parolanın insan davranışlarından, sızdırılmış parola kümelerinden ve saldırganların kullandığı tahmin stratejilerinden ne ölçüde etkilenebildiğiyle de değerlendirilmelidir.

Parola güvenliği literatürü genel olarak dört ana başlık altında incelenebilir. Birinci grup çalışmalar, insan seçimi parolaların istatistiksel özelliklerini ve kullanıcı davranışlarını analiz eder. İkinci grup çalışmalar, saldırgan bakış açısıyla parola tahmin modelleri geliştirir. Bu modeller sözlük saldırıları, Markov modelleri, olasılıksal bağlamdan bağımsız gramerler, kural tabanlı genişletmeler ve modern derin öğrenme yaklaşımlarını kapsar. Üçüncü grup çalışmalar, parola güç ölçerleri ve kullanıcıya geri bildirim veren sistemleri değerlendirir. Dördüncü grup ise parola üretimi, öneri sistemleri ve kullanıcıya daha güvenli parola oluşturma sürecinde rehberlik eden hibrit sistemlere odaklanır.

Bu proje, LSTM tabanlı parola tahmin edilebilirlik analizi ile kural tabanlı parola güvenliği değerlendirmesini birleştiren hibrit bir yaklaşım önermektedir. Böylece sistem yalnızca parolanın uzunluk, büyük/küçük harf, rakam ve özel karakter içerip içermediğini kontrol etmekle kalmaz; aynı zamanda parolanın öğrenilebilir karakter dizileri ve yaygın örüntüler açısından ne kadar tahmin edilebilir olduğunu da dikkate alır. Literatürdeki çalışmalar incelendiğinde, yalnızca kural tabanlı sistemlerin gerçek saldırgan davranışını yeterince temsil edemediği, yalnızca derin öğrenme tabanlı tahmin modellerinin ise kullanıcıya açıklanabilir ve uygulanabilir geri bildirim üretmekte sınırlı kalabildiği görülmektedir. Bu nedenle hibrit bir parola risk skorlama sistemi, hem güvenlik hem de kullanılabilirlik açısından daha dengeli bir yaklaşım sunmaktadır.

## 2. Parola Güvenliği ve Kullanıcı Davranışı

Parola güvenliği üzerine erken dönem çalışmalar, kullanıcıların parola seçimindeki zayıflıkları ve sistemlerin bu zayıflıkları nasıl kötüye kullanılabilir hâle getirdiğini göstermiştir. Morris ve Thompson’ın klasik çalışması, Unix sistemlerinde parola güvenliği sorunlarını ele alarak, zayıf parolaların sistem güvenliğini ciddi biçimde etkileyebileceğini göstermiştir [1]. Klein ise kullanıcıların sıkça tahmin edilebilir parolalar seçtiğini ve sözlük tabanlı saldırıların bu zayıflıkları kolayca kullanabildiğini ortaya koymuştur [2]. Bu çalışmalar, parola güvenliğinin yalnızca kriptografik saklama yöntemleriyle değil, kullanıcıların parola seçme davranışlarıyla da doğrudan ilişkili olduğunu göstermesi bakımından önemlidir.

Florêncio ve Herley, web parola alışkanlıklarını geniş ölçekli biçimde inceleyerek kullanıcıların farklı servislerde parola tekrarına, basit parola kullanımına ve hatırlanabilirlik odaklı seçimlere yöneldiğini göstermiştir [3]. Bonneau’nun yaklaşık 70 milyon kullanıcı parolasını analiz ettiği çalışma ise parola dağılımlarının teorik entropi varsayımlarından oldukça farklı olduğunu ve gerçek parolaların ağır kuyruklu bir dağılım sergilediğini göstermiştir [4]. Bu bulgu, güvenlik değerlendirmelerinde yalnızca karakter uzayı büyüklüğünü temel alan basit entropi hesaplarının yetersiz kalabileceğini göstermektedir.

Komanduri ve arkadaşları, parola oluşturma politikalarının kullanıcı davranışı üzerindeki etkisini incelemiş ve daha karmaşık parola politikalarının her zaman daha güvenli veya daha kullanılabilir sonuçlar doğurmadığını göstermiştir [5]. Kelley ve arkadaşları ise parola gücünü gerçek parola kırma algoritmalarını simüle ederek ölçmüş ve parola politikalarının güvenlik üzerindeki etkisinin saldırı modeline bağlı olarak değiştiğini ortaya koymuştur [6]. Bu çalışmalar, parola güvenliği değerlendirmesinde gerçekçi saldırı modellerinin ve kullanıcı davranışlarının birlikte ele alınması gerektiğini göstermektedir.

Kullanıcıların parola güvenliğini algılama biçimi de önemli bir araştırma alanıdır. Ur ve arkadaşları, kullanıcıların parolaların gerçek güvenliği ile algıladıkları güvenlik arasında fark olabileceğini göstermiştir [7]. Kullanıcılar çoğu zaman sembol veya rakam ekledikleri parolaların otomatik olarak güçlü olduğunu düşünmekte, ancak saldırganların yaygın dönüşüm kalıplarını bildiğini göz ardı etmektedir. Bu durum, parola güç ölçerlerinin yalnızca skor üretmesini değil, aynı zamanda kullanıcıya açıklanabilir ve doğru yönlendirici geri bildirim sunmasını gerekli kılmaktadır.

## 3. Geleneksel Parola Tahmin Yöntemleri

Parola tahmin saldırılarının erken dönemlerinde sözlük tabanlı yaklaşımlar yaygın biçimde kullanılmıştır. Bu yöntemlerde saldırganlar yaygın kelimeleri, isimleri, tarihleri, klavye örüntülerini ve sızdırılmış parola listelerini kullanarak aday parola kümeleri oluşturur. Narayanan ve Shmatikov, insan tarafından hatırlanabilir parolaların akıllı sözlük saldırılarına karşı savunmasız kalabileceğini ve zaman-bellek takası teknikleri ile büyük parola uzaylarının daha etkin taranabileceğini göstermiştir [8].

Daha sonra parola tahmininde olasılıksal modeller öne çıkmıştır. Weir ve arkadaşları, olasılıksal bağlamdan bağımsız gramerler kullanarak parola yapılarının öğrenilebileceğini göstermiştir [9]. PCFG yaklaşımı, parolaları harf, rakam ve sembol blokları gibi yapısal bileşenlere ayırarak en olası parola yapılarını önceliklendirir. Bu yöntem, yalnızca ham sözlük listelerine dayalı saldırılardan daha sistematik bir tahmin stratejisi sunar.

Markov modelleri de parola tahmininde yaygın kullanılan geleneksel yöntemlerden biridir. Ma ve arkadaşları, olasılıksal parola modellerinin değerlendirilmesine yönelik kapsamlı bir çalışma yapmış ve Markov modellerinin doğru yapılandırıldığında güçlü tahmin performansı sunabildiğini göstermiştir [10]. Dürmuth ve arkadaşlarının OMEN çalışması ise Markov tabanlı parola üretimini daha verimli hâle getirerek aday parolaları olasılık sırasına göre üretmeyi amaçlamıştır [11]. Bu yaklaşım, saldırganın en yüksek başarı ihtimali olan parolaları daha erken denemesini sağlar.

Geleneksel yöntemlerin en önemli avantajı açıklanabilir olmalarıdır. Örneğin PCFG modeli, bir parolanın hangi yapısal kalıba uyduğunu gösterebilir; Markov modelleri ise karakter geçiş olasılıkları üzerinden tahmin edilebilirliği yorumlayabilir. Ancak bu yöntemlerin sınırlılığı, karmaşık ve uzun bağımlılıkları yakalamakta zorlanmalarıdır. İnsan seçimi parolalar yalnızca yerel karakter geçişlerinden değil, kelime benzeri yapıların, kültürel kalıpların, tarihlerin, klavye düzenlerinin ve kişisel tercihlerin birleşiminden oluşabilir. Bu durum, derin öğrenme tabanlı modellerin parola tahmini alanına uygulanmasını motive etmiştir.

## 4. Parola Güç Ölçerleri ve Kural Tabanlı Yaklaşımlar

Parola güç ölçerleri, kullanıcı parola oluştururken anlık geri bildirim sunan sistemlerdir. Geleneksel güç ölçerler genellikle uzunluk, büyük harf, küçük harf, rakam ve özel karakter varlığı gibi basit kurallara dayanır. Ancak literatürde bu yaklaşımın önemli sınırlılıkları olduğu gösterilmiştir. Basit karakter kompozisyonu kuralları, kullanıcıları tahmin edilmesi kolay ancak biçimsel olarak karmaşık görünen parolalar oluşturmaya yöneltebilir. Örneğin “Password123!” gibi bir parola büyük harf, küçük harf, rakam ve sembol içerse de saldırganlar açısından oldukça tahmin edilebilir olabilir.

Wheeler’ın zxcvbn çalışması, parola güç tahmini alanında önemli bir dönüm noktasıdır [12]. zxcvbn, yalnızca karakter çeşitliliğine bakmak yerine yaygın parolaları, sözlük kelimelerini, klavye örüntülerini, tekrarları, tarihleri ve leetspeak dönüşümlerini tanıyan daha gerçekçi bir parola güç tahmin yaklaşımı sunmuştur. Bu çalışma, parola güç ölçerlerinin saldırgan davranışına yakın modeller kullanması gerektiğini göstermiştir.

Komanduri ve arkadaşlarının Telepathwords sistemi, kullanıcının parola yazma sürecinde sonraki karakteri tahmin etmeye çalışarak zayıf parolaları daha oluşturulma aşamasında engellemeyi amaçlamıştır [13]. Bu yaklaşım, parola güvenliğini yalnızca sonradan değerlendiren değil, kullanıcıyı parola oluşturma sürecinde yönlendiren bir sistem anlayışı sunar. Ur ve arkadaşları da veri odaklı parola ölçerlerin kullanıcıya daha eyleme geçirilebilir geri bildirim sunabileceğini göstermiştir [14].

Golla ve Dürmuth, parola güç ölçerlerinin doğruluğunu inceleyerek farklı ölçerlerin aynı parola için farklı sonuçlar verebildiğini göstermiştir [15]. Wang ve arkadaşları da modern parola güç ölçerlerinin doğruluğunu karşılaştırmış ve tek bir yaklaşımın tüm saldırı modellerine karşı yeterli olmayabileceğini vurgulamıştır [16]. Bu bulgular, parola güvenliği değerlendirmesinde tek boyutlu skorların yeterli olmadığını; kural tabanlı, veri odaklı ve model tabanlı bileşenlerin birlikte kullanılmasının daha güvenilir sonuçlar sağlayabileceğini göstermektedir.

## 5. Derin Öğrenme Tabanlı Parola Tahmini

Derin öğrenme modellerinin parola tahminine uygulanması, parola dizilerindeki karmaşık örüntüleri öğrenme potansiyeli nedeniyle önemli bir araştırma alanı hâline gelmiştir. Melicher ve arkadaşları, sinir ağları kullanarak parola tahmin edilebilirliğini modelleyen öncü çalışmalardan birini sunmuştur [17]. Bu çalışmada sinir ağlarının, özellikle yüksek tahmin sayılarında geleneksel yöntemlere kıyasla daha etkili olabileceği gösterilmiştir. Ayrıca modelin istemci tarafında çalışabilecek biçimde sıkıştırılabilmesi, parola güç ölçerlerinin pratik sistemlere entegre edilmesi açısından önemlidir.

LSTM ve genel olarak tekrarlayan sinir ağları, karakter dizileri üzerindeki uzun dönem bağımlılıkları modelleyebilme yetenekleri nedeniyle parola tahmini için uygundur. Parolalar doğal dil cümleleri kadar uzun olmasa da, kullanıcılar tarafından oluşturulan karakter dizileri belirli örüntüler içerir. Örneğin ad + yıl, kelime + sembol, klavye dizisi + rakam veya basit leetspeak dönüşümleri LSTM modelleri tarafından öğrenilebilir. Bu nedenle LSTM tabanlı modeller, yalnızca karakter çeşitliliğini değil, karakterlerin bağlamsal sırasını ve olasılıksal ilişkilerini de dikkate alabilir.

Zhang ve arkadaşlarının derin öğrenme tabanlı parola tahmini ve parola güç değerlendirmesi üzerine yaptığı derleme, RNN, LSTM, GAN ve diğer derin öğrenme yöntemlerinin parola alanında nasıl kullanıldığını sistematik olarak incelemiştir [18]. Bu derleme, derin öğrenme modellerinin hem parola tahmini hem de parola güç ölçümü için kullanılabileceğini, ancak eğitim verisi kalitesi, model genellemesi, etik veri kullanımı ve açıklanabilirlik gibi konuların hâlâ önemli zorluklar olduğunu vurgulamaktadır.

Derin öğrenme tabanlı yaklaşımların geleneksel yöntemlere göre temel avantajı, elle tanımlanmış kurallara daha az bağımlı olmalarıdır. Ancak bu durum aynı zamanda açıklanabilirlik sorununu beraberinde getirir. Bir LSTM modeli bir parolayı zayıf olarak değerlendirdiğinde, kullanıcının hangi karakter dizisi veya örüntü nedeniyle düşük skor aldığını anlaması zor olabilir. Bu nedenle yalnızca LSTM skoru kullanmak yerine, LSTM tahmin edilebilirlik skorunu kural tabanlı açıklanabilir bileşenlerle birleştirmek daha kullanışlı bir sistem tasarımı sunar.

## 6. GAN, Transformer ve Büyük Dil Modeli Tabanlı Yaklaşımlar

Derin öğrenmenin parola tahmini alanındaki etkisi yalnızca LSTM modelleriyle sınırlı değildir. Hitaj ve arkadaşları tarafından önerilen PassGAN, parola tahmini için üretici çekişmeli ağları kullanmıştır [19]. PassGAN, insan tarafından tasarlanmış parola üretim kurallarına ihtiyaç duymadan sızdırılmış parola kümelerinin dağılımını öğrenmeyi amaçlamıştır. Bu yaklaşım, parola tahmininde üretici modellerin kullanılabileceğini göstermesi bakımından önemli bir çalışmadır.

Bununla birlikte GAN tabanlı modellerin bazı sınırlılıkları vardır. GAN eğitim süreci kararsız olabilir, üretilen örneklerin çeşitliliği sınırlı kalabilir ve belirli koşullara göre parola üretmek zorlaşabilir. Bu nedenle daha yeni çalışmalar, Transformer ve büyük dil modeli tabanlı yaklaşımlara yönelmiştir. Xu ve arkadaşları tarafından önerilen PassBERT, çift yönlü Transformer mimarisini parola tahmini için kullanmış ve ön eğitim + ince ayar yaklaşımının parola tahmininde etkili olabileceğini göstermiştir [20]. Bu çalışma ayrıca hibrit parola güç ölçer yaklaşımının modern saldırılara karşı daha anlamlı değerlendirme sunabileceğini göstermesi bakımından bu proje ile kavramsal olarak ilişkilidir.

Rando ve arkadaşlarının PassGPT çalışması, büyük dil modellerinin parola modelleme ve yönlendirilmiş parola üretimi için kullanılabileceğini göstermiştir [21]. PassGPT, parola sızıntıları üzerinde eğitilen bir dil modeli olarak, GAN tabanlı yöntemlere kıyasla daha fazla daha önce görülmemiş parolayı tahmin edebildiğini bildirmiştir. Bu çalışma, parola modellemenin doğal dil işleme yöntemlerinden giderek daha fazla etkilendiğini göstermektedir.

Transformer ve LLM tabanlı yöntemler güçlü performans sunmakla birlikte, pratik parola güvenliği sistemlerinde bazı zorluklar doğurur. Bu modellerin eğitimi maliyetlidir, veri gizliliği açısından dikkat gerektirir ve son kullanıcı sistemlerinde düşük gecikme ile çalıştırılması her zaman kolay değildir. Bu nedenle daha hafif LSTM tabanlı modeller, özellikle eğitim ve demo amaçlı akademik projelerde dengeli bir tercih olabilir. LSTM modeli, parola dizilerindeki örüntüleri öğrenirken, kural tabanlı risk motoru da sonuçları kullanıcıya açıklanabilir hâle getirir.

## 7. Parola Üretimi ve Güvenli Öneri Sistemleri

Parola güvenliği yalnızca zayıf parolaları tespit etmekten ibaret değildir; kullanıcıya daha güvenli alternatifler sunmak da önemlidir. Parola üreticileri genellikle rastgelelik, uzunluk, karakter çeşitliliği ve kullanıcı tercihleri gibi parametreleri dikkate alır. Ancak tamamen rastgele üretilen parolalar yüksek güvenlik sağlasa da kullanıcı tarafından hatırlanması zor olabilir. Buna karşılık kullanıcı tarafından kolay hatırlanabilen parolalar çoğu zaman tahmin edilebilir örüntüler içerir.

Bu nedenle modern parola öneri sistemleri güvenlik ve kullanılabilirlik arasında denge kurmalıdır. Bir sistem, kullanıcının zayıf parolasını analiz ederek hangi yönlerden zayıf olduğunu açıklayabilir ve ardından daha güvenli bir alternatif oluşturabilir. Bu alternatif, uzunluk, karakter çeşitliliği ve rastgelelik açısından güçlü olmalı; aynı zamanda yaygın kelime, tarih, tekrar ve klavye örüntüsü gibi zayıflıkları içermemelidir.

Jiang ve arkadaşlarının OMECDN çalışması, parola üretimini Markov enumerator ve discriminant network bileşenleriyle ele alarak parola üretim modellerinin gelişmeye devam ettiğini göstermektedir [22]. Atzori ve arkadaşları ise parola gücünü sosyal ağlarda yayılan kişisel bilgi bağlamında değerlendirerek, kullanıcıya ait açık bilgilerin parola güvenliği üzerinde etkili olabileceğini göstermiştir [23]. Bu tür çalışmalar, parola güvenliği değerlendirmesinde yalnızca karakter dizisini değil, bağlamsal ve kişisel bilgileri de dikkate almanın önemini göstermektedir.

Bu proje kapsamında geliştirilen güvenli parola öneri sistemi, rastgele parola üretimi ile güvenlik skorlama mekanizmasını birleştirmektedir. Üretilen parola yalnızca biçimsel kurallara göre değil, aynı zamanda hibrit risk skorlama sistemi aracılığıyla değerlendirilir. Böylece kullanıcıya sunulan önerinin gerçekten güçlü olup olmadığı sistem tarafından tekrar kontrol edilir.

## 8. Sistematik Derlemeler ve Alanın Genel Eğilimleri

Son yıllarda parola tahmini ve parola güç değerlendirmesi üzerine sistematik derleme çalışmaları artmıştır. Yu ve arkadaşları, 2016–2023 yılları arasında yayımlanan otuzdan fazla parola tahmin yöntemini inceleyerek trawling guessing ve targeted guessing gibi farklı saldırı türleri için bir sınıflandırma sunmuştur [24]. Bu derleme, parola tahmin alanının yalnızca genel parola dağılımlarını öğrenmekten, kullanıcıya veya bağlama özel hedefli tahminlere doğru genişlediğini göstermektedir.

Zhang ve arkadaşlarının derin öğrenme survey çalışması, parola tahmini ve parola güç değerlendirmesinde RNN, LSTM, GAN ve benzeri derin öğrenme modellerinin önemini vurgulamaktadır [18]. Bu tür derlemeler, literatürde güçlü modelleme yaklaşımlarının bulunduğunu; ancak açıklanabilirlik, gerçek zamanlı kullanım, kullanıcıya öneri üretme ve farklı skor bileşenlerini birleştirme konularında hâlâ araştırma boşlukları olduğunu göstermektedir.

Password strength meter alanındaki çalışmalar da benzer bir eğilime sahiptir. Wheeler’ın zxcvbn yaklaşımı, kural tabanlı ancak saldırgan davranışına daha yakın bir sistem sunarken [12], Melicher ve arkadaşları neural network tabanlı parola tahminini pratik bir strength meter yaklaşımıyla ilişkilendirmiştir [17]. Wang ve arkadaşları ise modern password strength meter sistemlerinin tek başına yeterli olmadığını ve farklı saldırı modelleri altında tutarlı değerlendirme üretmenin zor olduğunu göstermiştir [16]. Bu nedenle hibrit skorlayıcılar, farklı yöntemlerin güçlü yanlarını birleştirme potansiyeli taşımaktadır.

## 9. Geleneksel Yöntemler ile Derin Öğrenme Yaklaşımlarının Karşılaştırılması

Geleneksel parola tahmin yöntemleri, açıklanabilirlik ve düşük hesaplama maliyeti açısından avantajlıdır. PCFG modelleri parola yapılarını açık biçimde temsil eder; Markov modelleri karakter geçiş olasılıklarını hesaplayarak aday üretir; zxcvbn gibi sistemler yaygın desenleri ve sözlük eşleşmelerini yakalayabilir. Bu yöntemlerin dezavantajı, karmaşık ve uzun bağımlılıkları öğrenmekte sınırlı kalmaları ve yeni parola örüntülerine uyum sağlamak için elle tanımlanmış kurallara ihtiyaç duyabilmeleridir.

Derin öğrenme modelleri ise veri üzerinden örüntü öğrenebilir. LSTM modelleri karakter dizilerindeki sıralı bağımlılıkları yakalayabilir; GAN tabanlı modeller gerçek parola dağılımlarına benzeyen yeni adaylar üretebilir; Transformer ve LLM tabanlı modeller daha geniş bağlamları modelleyebilir. Ancak bu yöntemlerin dezavantajları arasında eğitim maliyeti, veri gereksinimi, açıklanabilirlik eksikliği ve güvenilir skor kalibrasyonu yer alır.

Bu nedenle hibrit yaklaşımlar literatürde giderek daha anlamlı hâle gelmektedir. Hibrit bir parola güvenlik sistemi, kural tabanlı modül ile açıklanabilir geri bildirim üretirken, LSTM veya benzeri model tabanlı bileşen ile tahmin edilebilirliği daha gerçekçi biçimde ölçebilir. Bu proje de bu çizgide konumlanmaktadır. Önerilen sistemde kural tabanlı skor, parola uzunluğu, karakter çeşitliliği, tekrarlar ve yaygın desenler gibi açık kuralları değerlendirirken; LSTM tabanlı skor, parolanın öğrenilmiş parola dağılımları açısından ne kadar tahmin edilebilir olduğunu ölçer. Son skor, bu iki bileşenin ağırlıklı birleşimiyle üretilir.

## 10. Literatürdeki Eksiklikler ve Bu Çalışmanın Konumu

Literatürdeki çalışmalar incelendiğinde birkaç temel eksiklik öne çıkmaktadır. İlk olarak, birçok parola güç ölçer sistemi yalnızca basit kompozisyon kurallarına dayanmaktadır. Bu sistemler kullanıcıya hızlı geri bildirim sağlasa da gerçek saldırgan davranışını yeterince temsil edemez. İkinci olarak, derin öğrenme tabanlı parola tahmin modelleri güçlü tahmin performansı sunsa da kullanıcıya açıklanabilir geri bildirim üretmekte sınırlı kalabilir. Üçüncü olarak, birçok çalışma parola tahmini veya parola gücü değerlendirmesine odaklanırken, güvenli parola önerisini aynı sistem içinde bütünleşik biçimde ele almaz. Dördüncü olarak, modern parola güvenliği sistemlerinde API, frontend ve kullanıcı deneyimi bütünlüğü çoğu akademik çalışmada uygulama düzeyinde ayrıntılı olarak ele alınmamaktadır.

Bu proje, söz konusu eksiklikleri azaltmayı amaçlayan bütünleşik bir sistem sunmaktadır. Sistem, LSTM tabanlı parola tahmin edilebilirlik analizini, kural tabanlı güvenlik değerlendirmesiyle birleştirerek 0–100 arası hibrit bir güvenlik skoru üretir. Ayrıca parola güvenlik seviyesini “Çok Zayıf”, “Zayıf”, “Orta”, “Güçlü” ve “Çok Güçlü” kategorileriyle kullanıcıya anlaşılır biçimde sunar. Bunun yanında güvenli parola öneri modülü sayesinde kullanıcıya yalnızca hata bildirmekle kalmaz, daha güvenli alternatif üretir. FastAPI tabanlı backend ve web arayüzü ile sistem, gerçek kullanıcı akışına uygun biçimde kullanılabilir hâle getirilir.

Bu yönüyle çalışma, geleneksel parola güç ölçerler ile derin öğrenme tabanlı parola tahmin modelleri arasında köprü kurmaktadır. Literatürdeki zxcvbn, Telepathwords, neural password guessing, PassGAN, PassBERT ve PassGPT gibi çalışmaların sunduğu bakış açıları dikkate alınarak, daha hafif, açıklanabilir ve uygulanabilir bir akademik prototip hedeflenmektedir. Proje, yüksek ölçekli saldırı sistemi geliştirmekten ziyade, parola güvenliğini kullanıcıya anlaşılır, ölçülebilir ve iyileştirilebilir biçimde sunmayı amaçlamaktadır.

## 11. Sonuç

Parola güvenliği literatürü, basit sözlük saldırılarından derin öğrenme ve büyük dil modeli tabanlı tahmin sistemlerine kadar geniş bir gelişim göstermiştir. Erken dönem çalışmalar kullanıcıların zayıf parola seçme eğilimlerini ortaya koyarken, PCFG ve Markov modelleri parola tahminini olasılıksal bir probleme dönüştürmüştür. zxcvbn ve Telepathwords gibi sistemler parola güç ölçerlerinin daha gerçekçi ve kullanıcı odaklı hâle gelmesine katkı sağlamıştır. LSTM, GAN, Transformer ve LLM tabanlı çalışmalar ise parola dizilerinin veri odaklı biçimde modellenebileceğini göstermiştir.

Bununla birlikte, yalnızca kural tabanlı veya yalnızca derin öğrenme tabanlı yaklaşımlar tek başına yeterli değildir. Kural tabanlı sistemler açıklanabilirlik sağlar ancak karmaşık örüntüleri kaçırabilir. Derin öğrenme modelleri güçlü tahmin performansı sunar ancak kullanıcıya anlaşılır geri bildirim vermekte zorlanabilir. Bu nedenle bu projede benimsenen hibrit yaklaşım, literatürdeki iki ana çizgiyi birleştirerek daha dengeli bir parola güvenliği değerlendirme sistemi sunmaktadır.

# Kaynakça

[1] R. Morris and K. Thompson, “Password Security: A Case History,” Communications of the ACM, vol. 22, no. 11, pp. 594–597, 1979.

[2] D. V. Klein, “Foiling the Cracker: A Survey of, and Improvements to, Password Security,” Proceedings of the 2nd USENIX Security Workshop, pp. 5–14, 1990.

[3] D. Florêncio and C. Herley, “A Large-Scale Study of Web Password Habits,” Proceedings of the 16th International Conference on World Wide Web, pp. 657–666, 2007.

[4] J. Bonneau, “The Science of Guessing: Analyzing an Anonymized Corpus of 70 Million Passwords,” Proceedings of the IEEE Symposium on Security and Privacy, pp. 538–552, 2012.

[5] S. Komanduri, R. Shay, P. G. Kelley, M. L. Mazurek, L. Bauer, N. Christin, L. F. Cranor, and S. Egelman, “Of Passwords and People: Measuring the Effect of Password-Composition Policies,” Proceedings of the SIGCHI Conference on Human Factors in Computing Systems, pp. 2595–2604, 2011.

[6] P. G. Kelley, S. Komanduri, M. L. Mazurek, R. Shay, T. Vidas, L. Bauer, N. Christin, L. F. Cranor, and J. Lopez, “Guess Again and Again and Again: Measuring Password Strength by Simulating Password-Cracking Algorithms,” Proceedings of the IEEE Symposium on Security and Privacy, pp. 523–537, 2012.

[7] B. Ur, F. Alfieri, M. Aung, L. Bauer, N. Christin, J. Colnago, L. F. Cranor, H. Dixon, P. Emami Naeini, H. Habib, N. Johnson, and W. Melicher, “Design and Evaluation of a Data-Driven Password Meter,” Proceedings of the CHI Conference on Human Factors in Computing Systems, pp. 3775–3786, 2017.

[8] A. Narayanan and V. Shmatikov, “Fast Dictionary Attacks on Passwords Using Time-Space Tradeoff,” Proceedings of the 12th ACM Conference on Computer and Communications Security, pp. 364–372, 2005.

[9] M. Weir, S. Aggarwal, B. de Medeiros, and B. Glodek, “Password Cracking Using Probabilistic Context-Free Grammars,” Proceedings of the IEEE Symposium on Security and Privacy, pp. 391–405, 2009.

[10] J. Ma, W. Yang, M. Luo, and N. Li, “A Study of Probabilistic Password Models,” Proceedings of the IEEE Symposium on Security and Privacy, pp. 689–704, 2014.

[11] M. Dürmuth, F. Angelstorf, C. Castelluccia, D. Perito, and A. Chaabane, “OMEN: Faster Password Guessing Using an Ordered Markov Enumerator,” International Symposium on Engineering Secure Software and Systems, pp. 119–132, 2015.

[12] D. L. Wheeler, “zxcvbn: Low-Budget Password Strength Estimation,” Proceedings of the 25th USENIX Security Symposium, pp. 157–173, 2016.

[13] S. Komanduri, R. Shay, L. F. Cranor, C. Herley, and S. Schechter, “Telepathwords: Preventing Weak Passwords by Reading Users’ Minds,” Proceedings of the 23rd USENIX Security Symposium, pp. 591–606, 2014.

[14] B. Ur, F. Alfieri, M. Aung, L. Bauer, N. Christin, J. Colnago, L. F. Cranor, H. Dixon, P. Emami Naeini, H. Habib, N. Johnson, and W. Melicher, “Design and Evaluation of a Data-Driven Password Meter,” Proceedings of the CHI Conference on Human Factors in Computing Systems, pp. 3775–3786, 2017.

[15] M. Golla and M. Dürmuth, “On the Accuracy of Password Strength Meters,” Proceedings of the ACM Conference on Computer and Communications Security, pp. 1567–1582, 2018.

[16] D. Wang, X. Shan, Q. Dong, Y. Shen, and C. Jia, “No Single Silver Bullet: Measuring the Accuracy of Password Strength Meters,” Proceedings of the USENIX Security Symposium, 2023.

[17] W. Melicher, B. Ur, S. M. Segreti, S. Komanduri, L. Bauer, N. Christin, and L. F. Cranor, “Fast, Lean, and Accurate: Modeling Password Guessability Using Neural Networks,” Proceedings of the 25th USENIX Security Symposium, pp. 175–191, 2016.

[18] T. Zhang, Z. Cheng, Y. Qin, Q. Li, and L. Shi, “Deep Learning for Password Guessing and Password Strength Evaluation: A Survey,” Proceedings of IEEE TrustCom, 2020.

[19] B. Hitaj, P. Gasti, G. Ateniese, and F. Pérez-Cruz, “PassGAN: A Deep Learning Approach for Password Guessing,” Proceedings of the International Conference on Applied Cryptography and Network Security, pp. 217–237, 2019.

[20] M. Xu, J. Yu, X. Zhang, C. Wang, S. Zhang, H. Wu, and W. Han, “Improving Real-World Password Guessing Attacks via Bi-Directional Transformers,” Proceedings of the 32nd USENIX Security Symposium, 2023.

[21] J. Rando, F. Pérez-Cruz, and B. Hitaj, “PassGPT: Password Modeling and Guided Generation with Large Language Models,” International Conference on Applied Cryptography and Network Security Workshops, 2023.

[22] J. Jiang, A. Zhou, L. Liu, and L. Zhang, “OMECDN: A Password-Generation Model Based on an Ordered Markov Enumerator and Critic Discriminant Network,” Applied Sciences, vol. 12, no. 23, article 12379, 2022.

[23] M. Atzori, G. Fenu, and M. Marras, “Evaluating Password Strength Based on Information Spread Across Multiple Social Networks,” Cyber Security and Applications, vol. 2, article 100030, 2024.

[24] W. Yu, Z. Li, and X. Wang, “A Systematic Review on Password Guessing Tasks,” Entropy, vol. 25, no. 9, article 1303, 2023.

[25] M. Dell’Amico and M. Filippone, “Monte Carlo Strength Evaluation: Fast and Reliable Password Checking,” Proceedings of the ACM Conference on Computer and Communications Security, pp. 158–169, 2015.

[26] C. Castelluccia, M. Dürmuth, and D. Perito, “Adaptive Password-Strength Meters from Markov Models,” Proceedings of the Network and Distributed System Security Symposium, 2012.

[27] D. Pasquini, A. Gangwal, G. Ateniese, M. Bernaschi, and M. Conti, “Improving Password Guessing via Representation Learning,” Proceedings of the IEEE Symposium on Security and Privacy, 2021.

[28] X. Guo, Z. Zhang, and Y. Guo, “Dynamic Markov Model: Password Guessing Using Probability Adjustment Method,” Applied Sciences, vol. 11, no. 10, article 4607, 2021.

[29] V. Zimmermann, K. Renaud, and N. Gerber, “Hybrid Password Meters for More Secure Passwords: A Comprehensive Study of Password Meters Including Nudges and Password Information,” Behaviour & Information Technology, 2022.

[30] D. Wang, Z. Zhang, P. Wang, J. Yan, and X. Huang, “Targeted Online Password Guessing: An Underestimated Threat,” Proceedings of the ACM Conference on Computer and Communications Security, 2016.

[31] D. Wang, X. Zhang, Z. Zhang, and P. Wang, “Understanding Security Failures of Multi-Factor Authentication Schemes for Multi-Server Environments,” Computers & Security, 2018.

[32] M. Bishop and D. V. Klein, “Improving System Security via Proactive Password Checking,” Computers & Security, vol. 14, no. 3, pp. 233–249, 1995.
