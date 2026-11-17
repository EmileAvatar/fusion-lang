Youtube: https://www.youtube.com/watch?v=6ausp1qPWfk
Title: Why Zig over Rust, C, C++, Odin, Nim, etc?



--- summary ---

## Why the speaker prefers Zig

- The choice is personal, not a claim that Zig is objectively better than Rust, C, or C++; the speaker favors the language whose trade-offs fit their priorities.  
- Zig’s explicitness and predictability appeal to the speaker because allocations, conversions, and control flow are visible rather than happening implicitly.  
- The speaker sees learning Zig as a way to become a better developer: its approach has made them wish they were using it when working in other languages, though they acknowledge exceptions.  

## Trade-offs with other languages

- **Rust:** The speaker values Rust’s strong safety guarantees but finds its borrow checker, ownership model, tooling, and language complexity add friction to low-level programming; they prefer Zig’s style and compile-time programming.    
- **C++:** The speaker finds C++ difficult to work with because its legacy, complex standards, and build systems create friction; they also dislike exceptions, templates, and complicated overload resolution.  
- **C:** C offers direct control, but the speaker wants more help with safety and error handling than C provides; they prefer errors represented as values over exceptions.    
- **Nim:** The speaker likes that Nim can target C or JavaScript, but its move toward more Python-like syntax puts them off because they dislike Python’s style.    
- **Clojure:** The speaker had trouble finding Clojure jobs, although they acknowledge employability is an inconsistent reason to reject it because they are not currently seeking a Zig job either.  
- These judgments reflect individual preferences and circumstances, not universal rankings of the languages.    

## Zig’s practical appeal

- Zig can interoperate with C, which lets programmers draw on the C ecosystem; the speaker describes using Zig to orchestrate ImageMagick for image manipulation.    
- Zig brings the compiler, build system, formatter, package-fetching tool, and cross-compilation support into one toolchain; the speaker values this because coordinating many separate tools can become cumbersome.    
- Zig uses manual memory management, but makes allocations explicit, testable, and replaceable; the speaker values this as a way to control memory without C’s perceived pitfalls.    
- With no hidden runtime, the speaker finds it easier to reason about what a binary contains, how errors propagate, and how performance behaves.  
- Zig’s compile-time execution runs ordinary Zig code, which the speaker finds more straightforward than C++ templates or Rust macros for metaprogramming.  
- Runtime safety checks are selectable rather than tied to one mandatory model; different build modes, including debug, safe, fast, and small, let developers choose between checking behavior during development and optimizing shipped builds.


--- transcribe ---

 A couple of days ago I put out this video talking about how I'm locking in on Zig going forward. One of the most common comments or style of comments really was why not my favorite language. Why not this other language that I think is really interesting. Why not Rust? Why not C? Why not C++? Why not Odin? So many different options. And why not Nim was another one which is I find funny but for an inside reason. I want to talk about those those comments

today because I started writing out responses for people and then I realized it was going to be very duplicative and some people asked the same question like to a T. Like why not C++ over and over again. Um why not Rust was pretty common as well but I just wanted to talk about that because I think that's an important thing to talk about. And before we get started the key takeaway for this is really really simple. It's my own choice. Rust is not better

than Zig. Zig is not better than Rust. C++ is not better than Zig. Zig's not better than C++. My opinion may differ but the reality of it is that I'm biased in my choices and this is why it's the right choice for me. You may think that my reasoning is not valid and it might not be for you. Congratulations, that's how life works. Okay, cool. Let's get into it. So yeah, without a doubt the two most

common ones were why not Rust and why not C++. So um why not Rust, right? So Rust is Rust is a really excellent language. It gives you those airtight safety guarantees and those guarantees come with some friction. Specifically the borrow checker. There's also heavier tooling that comes with it generally a more complex language than Zig and a larger ecosystem that you must buy into which you know has pros and cons. I want to work with low-level programming without the gymnastics that come with the ownership model.

And to be completely honest with you, I struggled to write Rust before I wrote Zig. And now that I've written so much Zig, I do feel like I could take the concepts I've learned and actually have a much better time writing Rust. But I I just don't want to at this point. I would rather write Zig. I find it to be a more pleasurable language to work at. I like the explicitness of Zig. And additionally compile time feels so much nicer than macros

in in Rust in particular but that's also a really good segue into C++. Macros in C++ templates are awful in my opinion. Um but in addition to that C++ is this huge inconsistent behemoth that carries like really decades of legacy. The language and the standard are extremely complex. The build systems are extremely painful. And Zig just tends to reject this complexity. There's no implicit behavior. There's no exceptions which I have a lot of thoughts on exceptions in general. I think they're a really

terrible practice. And like I mentioned there's no templates as a meta programming type solution. And there's also no undefined overload resolution rules where you don't have to worry about overloading in Zig. So another question that came up was why not C? This is pretty similar to the C++ one. C is going to give you that full control but it doesn't give you any help and I like the help. With C undefined behavior is everywhere. And the error handling story is weak

just like C++. Again, I don't like exceptions. That's one thing I'll give Rust over those two is Rust's errors as values is is much much preferable to exceptions for me. And honestly, I I can't really I struggle to understand why people would want exceptions over errors as values. Um my hunch is the people who want exceptions over errors as values have not been programming long and they feel like errors as values get in the way where exceptions are out of

the way. They're out of sight, out of mind. And that also means that you generally don't handle them very well or new new devs I should say don't handle them very well. Another one was why not Nim? That one was brought up. I've been talking with a couple friends about Nim for a while now. It's an interesting language to me. I like that it is an abstraction over the compilation target. So you can compile Nim down to C or you can compile it to JavaScript

and I think they're working on Wasm. Nim actually had my attention a long time ago and this is maybe a little pedantic all puns intended or pi-dantic I guess. But Nim 2.0 made a syntax switch syntax swap to be more Pythonic and I cannot stand Python. I have a lot of reasons for that. Maybe that's a topic for another time. A really fun long deep dive fireside chat maybe. But um yeah, I can't stand Python. So the fact

that it looks more like Python than before makes me not want to use it more than before. I have similar feelings about Scala 3 for what it's worth. I really like Scala 2. It was one of my favorite languages. Scala 3 embraced Pythonic style and I do think that Scala 3 is probably a better version of Python but it's still trying to be Pythonic and I I just don't like it. So yeah, this brings us basically full circle. One more question

was why not Closure? Um I employability I guess. I The flip side is that Zig also doesn't seem super employable at the moment. So maybe that's a bad answer a bad a bad excuse a bad response. But the fact of the matter is that with Closure I do feel like um I feel like I had a hard time finding Closure jobs at the time. The world was different then. Remote work wasn't as popular. Things may have changed but also like if that's my argument I'm not

looking for a Zig job at the moment either. I'm happy where I'm at and I am um learning Zig and embracing it as something to make me a better developer. And I think really that's what it boils down to is I feel like Zig is going to help me become a better version of myself before learning Zig. And I've seen that too, right? Like I've been learning Zig for about a year now off and on with other languages thrown in. The more I swap to other languages

the more I'm like, "Wow, I wish this was Zig that I was writing instead." Some exceptions apply. Results may vary. Consult your doctor before swapping to Zig. So so why Zig, right? So I've mentioned this a little bit. I've hinted towards this I should say. There's the explicitness and predictability you get with Zig. Almost nothing really happens behind your back. Everything is really right in front of you. There's no hidden allocations, no hidden coercions. No

implicit control flow. Explicit is nice. I I like that. You can interop with C, right? So one of the things I really liked about Closure was the adoption of Closure felt like it had a a boon by being built on top of the JVM and having really good really good Java interop. In Closure anytime you interop with Java the Java code was the interop was very obvious because it was doing things that like were not a Closure way to do things but

you could do it. This gives us access to the entire C ecosystem. I've done a video on interoping with C using um Oh my gosh. Not FFmpeg. My my ImageMagick. Sorry, my mind was blanking on what I ended up doing. Yeah, so using ImageMagick and orchestrating ImageMagick from Zig to do some image manipulation. Um and it it works out really really great. I also this is maybe another pedantic excuse reason but Go has made me

love the idea that there is a tool one tool for everything I should say. And Zig embraces that pretty well as as well. So the Zig compiler is your build system. There's a formatter that's built into it. There's a package manager through Zig fetch. It's got a cross compilation tool and on top of that cross compiling is really a first class feature and it's not some hack that's thrown into the build system. I like having all these things together. Coming from the JavaScript ecosystem

where I have to install a plethora of tools and make sure they all play well together. So like prettier and ESLint and TS TypeScript and setting up my TSConfig and all of that works but it starts to get weird when you wrap it all up in Webpack and Webpack is using Babel and you have to use the appropriate Babel plugin that matches the version of Webpack with the version of whatever plugin you're plugging into Babel and it's it's it's a nightmare. I hate it.

It was literally one of the reasons that I stopped wanting to do front end development. And I found Go and I was like, "Wow, this is so much better." And I've realized since that many languages are taking this approach. Many modern languages. Dart does a really good job of this. Go, Rust, Zig, you know, there's a plethora of others. The memory management of Zig is manual but it's structured so you kind of get this weird mix between Rust and C in a

bit of a way in a bit of a weird way. So you have that manual memory management you'd get of C but you get some of the safety not some of the safety. You get safety in a way that Rust is also providing safety. They're very different in the way that they provide safety. But with Zig your allocations are explicit. They're testable. They're swappable. You can control really those allocations without C's foot guns which is appealing to me. It

should be appealing to a lot of people I think. With Zig there's also So hidden runtime so it's easy to understand what your binary contains, how errors propagate, and really how to reason about performance. I mentioned this a little bit talking about Rust, but the meta programming in Zig is so simple. So Zig uses compile time execution of regular Zig code instead of C++ templates or Rust macros. It's powerful, but honestly it's it's also really straightforward. If you've not written a

Rust macro before or C++ template, I highly recommend trying it. It is a very wild experience compared to writing Rust or C++ respectively. And if you write compile time in Zig and try to build something similar in compile time, I think you'll find a much more pleasurable experience. Lastly, with Zig safety is opt-in, but it's not necessarily mandatory. You can add bounds checking, undefined behavior detection, and other runtime safety features without adopting a full Rust-like model. This is seen pretty

heavily through the different release modes that Zig provides, so you can do a debug release, you can release fast, you can release small. You have a lot of different options, and really safe is being the the fourth one that I I just omitted for some reason. But you get the flexibility to define how that works, and from the same code base you can take different approaches. So if you're building locally, you might be building in a debug release mode to test things

out. But when you're ready to ship things to customers and you you know, things are proven to work, you might build in release fast or release small and ship that to customers or whoever is using your your product or your code base. It doesn't necessarily have to be a product. That's really my feelings. Again, these are my own feelings. Everyone has different feelings for why they would want something, why they wouldn't want something, and it's really your world view and your biases that

lean you towards one of these topics over the other. Mine are leaning me towards Zig because the things that I value are also the things that Zig chooses to embrace. There are other languages that embrace some of those things. There are other languages that don't embrace any of those things. And you know, it leans me more towards Zig than other languages. Hopefully this was helpful. I really love the questions, especially why choose something over something else. So feel free to ask any question like that

anytime in the comments below, and I'll do my best to give you an answer. And if I can't write something in text because it ends up being too much to post on YouTube as a comment reply, you'll get a video out of it, probably. No no no promises, but I'd like to. I think that's it. So thank you very much for taking the time to listen to me. As always, I really appreciate it. And I hope you have a fantastic day.
